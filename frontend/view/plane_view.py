from email import header
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QScrollArea,
    QMessageBox,
    QGridLayout,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QLinearGradient, QPalette, QColor, QBrush

from .plane_card import PlaneCard
from .image_loader import ImageLoader
from .plane_details_dialog import PlaneDetailsDialog
from PySide6.QtGui import QIcon
from .plane_stats_dialog import PlaneStatsDialog


# --------------------------
# Cache פשוט לתמונות
# --------------------------
class SimpleCache:
    def __init__(self):
        self.cache = {}  # כתובת → QPixmap


class PlaneView(QWidget):
    def __init__(self, presenter):
        super().__init__()
        self.presenter = presenter
        self.presenter.view = self

        # ניהול תמונות (cache)
        self.cache_manager = SimpleCache()

        # מאפייני חלון
        self.setWindowTitle("FlySmart | Plane Manager")
        self.setWindowIcon(QIcon("frontend/assets/icons/airplane.svg"))
        self.resize(1200, 780)

        # רקע תכלת בהיר מדורג
        palette = QPalette()
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor("#FFFFFF"))
        grad.setColorAt(1, QColor("#EAF5FA"))
        palette.setBrush(QPalette.Window, QBrush(grad))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # עיצוב כללי
        self.setStyleSheet(
            """
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
                padding: 8px 32px 8px 12px;
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
        """
        )

        self.init_ui()
        self.presenter.load_planes()

    # ============================================================
    # בניית המסך הראשי
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

        # --- כפתור הצגת דיאגרמות ---
        self.stats_button = QPushButton("Show Statistics")
        self.stats_button.setObjectName(
            "addBtn"
        )  # כדי לקבל את אותו סגנון כמו Add Plane
        self.stats_button.clicked.connect(self.show_stats_dialog)
        header.addWidget(self.stats_button)

        # רווח קטן בין הכפתורים
        header.addSpacing(8)

        # --- כפתור הוספת מטוס ---
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

        # --- גריד הכרטיסים בתוך Scroll ---
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

    # ------------------------------------------------------------
    def show_status(self, text):
        """עדכון טקסט הסטטוס התחתון"""
        self.status_label.setText(f"Status: {text}")

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
        self.show_status(f"✅ Loaded {len(planes)} planes")
        if (
            hasattr(self, "stats_dialog")
            and self.stats_dialog
            and self.stats_dialog.isVisible()
        ):
            self.stats_dialog.update_charts(planes)

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
            match_name = (
                search_text in p.Name.lower() or search_text in p.MadeBy.lower()
            )
            match_maker = maker == "All Manufacturers" or p.MadeBy == maker
            match_year = year == "All Years" or str(p.Year) == year
            if match_name and match_maker and match_year:
                filtered.append(p)

        self.display_cards(filtered)
        # אם חלון הדיאגרמות פתוח — נעדכן אותו בזמן אמת
        if (
            hasattr(self, "stats_dialog")
            and self.stats_dialog
            and self.stats_dialog.isVisible()
        ):
            self.stats_dialog.update_charts(filtered)

    def reset_filters(self):
        self.search_input.clear()
        self.made_by_combo.setCurrentIndex(0)
        self.year_combo.setCurrentIndex(0)
        self.apply_filters()

    # ============================================================
    # הצגת כרטיסים
    # ============================================================
    def display_cards(self, planes):
        """מציגה כרטיסים בהדרגה כדי לשפר ביצועים"""
        # נקה קודם
        for i in reversed(range(self.cards_layout.count())):
            w = self.cards_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        # הגדר תור טעינה
        self._pending_planes = list(planes)
        self._current_index = 0

        def load_next_batch():
            if not hasattr(self, "_pending_planes"):
                return

            batch_size = 6
            planes_to_load = self._pending_planes[
                self._current_index : self._current_index + batch_size
            ]
            if not planes_to_load:
                return

            for plane in planes_to_load:
                card = PlaneCard(plane, self.cache_manager, self.presenter)
                card.clicked.connect(lambda p=plane: self.open_plane_details(p))
                row, col = divmod(self._current_index, 3)
                self.cards_layout.addWidget(card, row, col)
                self._current_index += 1

            if self._current_index < len(self._pending_planes):
                QTimer.singleShot(150, load_next_batch)

        load_next_batch()

    # ============================================================
    # פתיחת חלון פרטים
    # ============================================================
    def open_plane_details(self, plane):
        if hasattr(self, "active_details_dialog") and self.active_details_dialog:
            try:
                self.active_details_dialog.close()
            except Exception:
                pass

        dialog = PlaneDetailsDialog(self, plane, self.cache_manager, self.presenter)
        self.active_details_dialog = dialog
        dialog.exec()
        self.active_details_dialog = None

    # ============================================================
    # פונקציות עזר לעדכון כרטיסים
    # ============================================================
    def add_plane_card(self, plane):
        """מוסיפה כרטיס חדש של מטוס"""
        card = PlaneCard(plane, self.cache_manager, self.presenter)
        card.clicked.connect(lambda p=plane: self.open_plane_details(p))
        total = self.cards_layout.count()
        row, col = divmod(total, 3)
        self.cards_layout.addWidget(card, row, col)
        self.show_status(f"✅ Plane '{plane.Name}' added.")

    def refresh_plane_card(self, updated_plane):
        """מרעננת כרטיס לאחר עריכה"""
        for i in range(self.cards_layout.count()):
            w = self.cards_layout.itemAt(i).widget()
            if hasattr(w, "plane") and w.plane.PlaneId == updated_plane.PlaneId:
                w.plane = updated_plane
                w._fade_in_image(None)
                w.repaint()
                break
        self.show_status(f"✏️ Plane '{updated_plane.Name}' updated.")

    def remove_plane_card(self, plane_id):
        """מסירה כרטיס לאחר מחיקה"""
        for i in reversed(range(self.cards_layout.count())):
            w = self.cards_layout.itemAt(i).widget()
            if hasattr(w, "plane") and w.plane.PlaneId == plane_id:
                w.deleteLater()
                break
        self.show_status("🗑️ Plane deleted successfully.")

    def show_stats_dialog(self):
        """פותח את חלון הדיאגרמות או מרענן אם כבר פתוח"""
        planes = self.presenter.get_displayed_planes()

        # אם החלון כבר פתוח — רק נרענן אותו
        if (
            hasattr(self, "stats_dialog")
            and self.stats_dialog
            and self.stats_dialog.isVisible()
        ):
            self.stats_dialog.update_charts(planes)
            self.stats_dialog.raise_()
            self.stats_dialog.activateWindow()
        else:
            # אם לא פתוח — ניצור אחד חדש
            self.stats_dialog = PlaneStatsDialog(planes, self)
            self.stats_dialog.show()

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)
