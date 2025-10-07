from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QScrollArea, QFrame, QGridLayout, QMessageBox,
    QDialog, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QSize, QThread, Signal, QObject, QPropertyAnimation, QRect
from PySide6.QtGui import QPixmap, QLinearGradient, QPalette, QColor, QBrush
import requests
from io import BytesIO


# === טעינת תמונות אסינכרונית עם QThread ===
class ImageLoader(QObject):
    finished = Signal(str, bytes)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def load(self):
        """מוריד תמונה ברקע ושולח bytes בלבד (לא QPixmap)"""
        data = None
        try:
            if self.url.startswith("http"):
                response = requests.get(self.url, timeout=5)
                if response.status_code == 200:
                    data = response.content
            else:
                with open(self.url, "rb") as f:
                    data = f.read()
        except Exception:
            pass
        # שולחים רק bytes, לא QPixmap → בטוח לגמרי
        self.finished.emit(self.url, data)


class PlaneView(QWidget):
    def __init__(self, presenter):
        super().__init__()
        self.presenter = presenter
        self.presenter.view = self

        # cache לתמונות + ניהול threads/loaders
        self.image_cache = {}
        self._threads = []
        self._loaders = []

        self.setWindowTitle("FlySmart | Plane Manager")
        self.resize(1200, 780)

        # === רקע תכלת-כחלחל ===
        palette = QPalette()
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor("#FFFFFF"))
        grad.setColorAt(1, QColor("#EAF5FA"))
        palette.setBrush(QPalette.Window, QBrush(grad))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # === עיצוב כללי ===
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                color: #1A1F1D;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: 600;
                color: #1A2C3A;
            }
            QPushButton#addBtn {
                background-color: #4BA3C7;
                color: white;
                border-radius: 10px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton#addBtn:hover { background-color: #3A94B8; }

            QLineEdit, QComboBox {
                background-color: white;
                border: 1px solid #D5E7EE;
                border-radius: 10px;
                padding: 8px 12px;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #D5E7EE;
                border-radius: 10px;
                padding: 8px 32px 8px 12px;  /* מרווח נוסף מימין לחץ */
                min-width: 140px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 22px;
                border: none;
                border-left: 1px solid #D5E7EE;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                background-color: #F5FAFC;
            }

            QComboBox::down-arrow {
                image: url(frontend/assets/icons/arrow_down.svg);
                width: 10px;
                height: 10px;
                margin-right: 6px;
            }
            QComboBox::down-arrow:on {  /* בעת לחיצה */
                image: url(frontend/assets/icons/arrow_down_pressed.svg);
            }

            QPushButton#clearBtn {
                background-color: #E8F4F8;
                color: #4BA3C7;
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton#clearBtn:hover { background-color: #D7EEF3; }

            QLabel#status {
                background-color: #F5FAFC;
                border-top: 1px solid #D5E7EE;
                color: #3C4E56;
                padding: 8px 14px;
            }
        """)

        self.init_ui()
        self.presenter.load_planes()

    # ============================================================
    # מבנה המסך
    # ============================================================
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # --- כותרת עליונה ---
        header = QHBoxLayout()
        title = QLabel("Plane Manager")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        add_btn = QPushButton("+ Add Plane")
        add_btn.setObjectName("addBtn")
        add_btn.clicked.connect(self.presenter.open_add_plane)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # --- אזור סינון ---
        filters = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or manufacturer...")
        self.search_input.textChanged.connect(self.apply_filters)
        self.made_by_combo = QComboBox()
        self.made_by_combo.addItem("All Manufacturers")
        self.made_by_combo.currentTextChanged.connect(self.apply_filters)
        self.year_combo = QComboBox()
        self.year_combo.addItem("All Years")
        self.year_combo.currentTextChanged.connect(self.apply_filters)
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("clearBtn")
        clear_btn.clicked.connect(self.reset_filters)
        filters.addWidget(self.search_input, 3)
        filters.addWidget(self.made_by_combo)
        filters.addWidget(self.year_combo)
        filters.addWidget(clear_btn)
        layout.addLayout(filters)

        # --- Scroll + גריד של כרטיסים ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        container = QWidget()
        self.cards_layout = QGridLayout(container)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        self.cards_layout.setSpacing(18)
        self.cards_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.scroll.setWidget(container)
        layout.addWidget(self.scroll)

        # --- שורת סטטוס ---
        self.status_label = QLabel("Status: ⏳ Loading...")
        self.status_label.setObjectName("status")
        layout.addWidget(self.status_label)

    # ============================================================
    # הצגת רשימת מטוסים
    # ============================================================
    def show_planes(self, planes):
        self.planes = planes
        makers = sorted(set(p.MadeBy for p in planes if p.MadeBy))
        years = sorted(set(str(p.Year) for p in planes if p.Year))
        self.made_by_combo.blockSignals(True)
        self.year_combo.blockSignals(True)
        self.made_by_combo.clear()
        self.made_by_combo.addItem("All Manufacturers")
        self.made_by_combo.addItems(makers)
        self.year_combo.clear()
        self.year_combo.addItem("All Years")
        self.year_combo.addItems(years)
        self.made_by_combo.blockSignals(False)
        self.year_combo.blockSignals(False)
        self.apply_filters()
        self.status_label.setText(f"Status: ✅ Loaded {len(planes)} planes")

    # ============================================================
    # סינון
    # ============================================================
    def apply_filters(self):
        if not hasattr(self, "planes"):
            return

        search_text = self.search_input.text().strip().lower()
        maker = self.made_by_combo.currentText()
        year = self.year_combo.currentText()

        filtered = []
        for p in self.planes:
            match_name = search_text in p.Name.lower() or search_text in p.MadeBy.lower()
            match_maker = maker == "All Manufacturers" or p.MadeBy == maker
            match_year = year == "All Years" or str(p.Year) == year
            if match_name and match_maker and match_year:
                filtered.append(p)

        self.display_cards(filtered)

    def reset_filters(self):
        self.search_input.clear()
        self.made_by_combo.setCurrentIndex(0)
        self.year_combo.setCurrentIndex(0)
        self.apply_filters()

    # ============================================================
    # הצגת כרטיסים
    # ============================================================
    def display_cards(self, planes):
        for t in list(self._threads):
            try:
                t.quit()
                t.wait()
            except Exception:
                pass
        self._threads.clear()
        self._loaders.clear()

        for i in reversed(range(self.cards_layout.count())):
            w = self.cards_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        for idx, plane in enumerate(planes):
            card = self.create_plane_card(plane)
            row, col = divmod(idx, 3)
            self.cards_layout.addWidget(card, row, col)

        for i in range(3):
            spacer = QWidget()
            spacer.setFixedSize(340, 290)
            self.cards_layout.addWidget(spacer, len(planes)//3 + 1, i)

    # ============================================================
    # יצירת כרטיס יחיד (עם hover אמיתי)
    # ============================================================
    def create_plane_card(self, plane):
        card = QFrame()
        card.setObjectName("card")
        card.setCursor(Qt.PointingHandCursor)
        card.setFixedSize(340, 290)
        card.mousePressEvent = lambda e, p=plane: self.show_plane_card(p)

        # צל רך
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 20))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # אזור תמונה
        img_container = QFrame()
        img_container.setStyleSheet("background-color: #F8FBFD; border-radius: 12px;")
        img_layout = QVBoxLayout(img_container)
        img_layout.setContentsMargins(8, 8, 8, 8)

        img = QLabel()
        img.setFixedSize(QSize(260, 150))
        img.setAlignment(Qt.AlignCenter)
        img.setPixmap(QPixmap("frontend/assets/icons/airplane.svg"))
        img_layout.addWidget(img, alignment=Qt.AlignCenter)
        layout.addWidget(img_container, alignment=Qt.AlignCenter)

        # טעינה אסינכרונית עם fade-in
        if plane.Picture:
            if plane.Picture in self.image_cache:
                pix = self.image_cache[plane.Picture]
                self._fade_in_image(img, pix)
            else:
                loader = ImageLoader(plane.Picture)
                thread = QThread(self)
                loader.moveToThread(thread)
                self._loaders.append(loader)
                self._threads.append(thread)
                loader.finished.connect(lambda url, data: self._update_image(img, url, data))
                loader.finished.connect(thread.quit)
                loader.finished.connect(loader.deleteLater)
                loader.finished.connect(lambda *_: self._safe_remove_loader(loader))
                thread.finished.connect(thread.deleteLater)
                thread.finished.connect(lambda: self._safe_remove_thread(thread))
                thread.started.connect(loader.load)
                thread.start()

        # כותרת ושורה שנייה
        name = QLabel(plane.Name)
        name.setObjectName("cardTitle")
        name.setAlignment(Qt.AlignCenter)
        layout.addWidget(name)

        info = QLabel(f"{plane.MadeBy} · {plane.Year} · Seats: {plane.NumOfSeats1 + plane.NumOfSeats2 + plane.NumOfSeats3}")
        info.setObjectName("cardSub")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        # עיצוב בסיסי
        card.setStyleSheet("""
            QFrame#card {
                background-color: white;
                border-radius: 18px;
                border: 1px solid #D8E8EE;
            }
            QLabel#cardTitle {
                font-size: 16px;
                font-weight: 600;
                color: #1A2C3A;
            }
            QLabel#cardSub {
                font-size: 13px;
                color: #5A6D78;
            }
        """)

        # --- אפקט hover עם אנימציה אמיתית ---
        def enterEvent(event):
            anim = QPropertyAnimation(card, b"geometry")
            anim.setDuration(180)
            anim.setStartValue(card.geometry())
            g = card.geometry()
            anim.setEndValue(g.adjusted(-3, -3, 3, 3))
            anim.start()
            card._hover_anim = anim
            super(QFrame, card).enterEvent(event)

        def leaveEvent(event):
            anim = QPropertyAnimation(card, b"geometry")
            anim.setDuration(180)
            g = card.geometry()
            anim.setStartValue(g)
            anim.setEndValue(g.adjusted(3, 3, -3, -3))
            anim.start()
            card._hover_anim = anim
            super(QFrame, card).leaveEvent(event)

        card.enterEvent = enterEvent
        card.leaveEvent = leaveEvent

        return card

    # ============================================================
    # Utility
    # ============================================================
    def _fade_in_image(self, label, pixmap):
        label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        opacity = QGraphicsOpacityEffect()
        label.setGraphicsEffect(opacity)
        anim = QPropertyAnimation(opacity, b"opacity")
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()
        label._fade_anim = anim

    def _update_image(self, label, url, data):
        """נקראת רק ב־UI thread — בונה כאן את ה־QPixmap"""
        if not data:
            return
        pix = QPixmap()
        pix.loadFromData(data)
        if pix.isNull():
            return
        self.image_cache[url] = pix
        self._fade_in_image(label, pix)

    def _safe_remove_thread(self, thread):
        try:
            if thread in self._threads:
                self._threads.remove(thread)
        except Exception:
            pass

    def _safe_remove_loader(self, loader):
        try:
            if loader in self._loaders:
                self._loaders.remove(loader)
        except Exception:
            pass

    # ============================================================
    # Popup של פרטים
    # ============================================================
    def show_plane_card(self, plane):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"✈ {plane.Name} – Details")
        dialog.setModal(True)
        dialog.setFixedSize(400, 420)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 16px;
            }
            QLabel {
                font-family: 'Segoe UI';
                color: #1A2C3A;
            }
            QLabel#header {
                font-size: 20px;
                font-weight: bold;
                color: #4BA3C7;
            }
            QPushButton {
                background-color: #4BA3C7;
                color: white;
                border-radius: 8px;
                padding: 6px 14px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #3A94B8; }
        """)

        vbox = QVBoxLayout(dialog)
        vbox.setAlignment(Qt.AlignTop)

        title = QLabel(f"✈ {plane.Name}")
        title.setObjectName("header")
        title.setAlignment(Qt.AlignCenter)
        vbox.addWidget(title)

        img = QLabel()
        img.setFixedSize(QSize(300, 180))
        img.setAlignment(Qt.AlignCenter)
        pix = self.image_cache.get(plane.Picture)
        if not pix and plane.Picture:
            try:
                if plane.Picture.startswith("http"):
                    response = requests.get(plane.Picture, timeout=5)
                    if response.status_code == 200:
                        pix = QPixmap()
                        pix.loadFromData(BytesIO(response.content).read())
                else:
                    pix = QPixmap(plane.Picture)
            except Exception:
                pix = None
        if pix:
            img.setPixmap(pix.scaled(img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            img.setPixmap(QPixmap("frontend/assets/icons/plane.svg"))
        vbox.addWidget(img, alignment=Qt.AlignCenter)

        info = QLabel(
            f"<b>Manufacturer:</b> {plane.MadeBy}<br>"
            f"<b>Year:</b> {plane.Year}<br>"
            f"<b>Total Seats:</b> {plane.NumOfSeats1 + plane.NumOfSeats2 + plane.NumOfSeats3}"
        )
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        vbox.addWidget(info)

        edit_btn = QPushButton("✏ Edit Plane")
        edit_btn.clicked.connect(lambda: self.presenter.open_edit_plane(plane))
        vbox.addWidget(edit_btn, alignment=Qt.AlignCenter)

        vbox.addStretch()
        dialog.exec()

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)
