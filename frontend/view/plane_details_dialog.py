from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QLinearGradient, QPalette, QBrush, QColor
import requests
from io import BytesIO


class PlaneDetailsDialog(QDialog):
    def __init__(self, parent, plane, cache_manager, presenter):
        super().__init__(parent)
        self.plane = plane
        self.cache = cache_manager
        self.presenter = presenter

        self.setWindowTitle(f"✈ {plane.Name} – Details")
        self.setModal(True)
        self.setFixedSize(480, 520)

        self._build_ui()

    # ------------------------------------------------------------
    def _build_ui(self):
        # רקע תכלת בהיר
        palette = QPalette()
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor("#F8FBFD"))
        grad.setColorAt(1, QColor("#EAF4F9"))
        palette.setBrush(QPalette.Window, QBrush(grad))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # כרטיס מרכזי
        card = QFrame()
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 18px;
                border: 1px solid #DCE8EE;
            }
        """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.addWidget(card, alignment=Qt.AlignCenter)

        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(40, 30, 40, 30)
        vbox.setSpacing(14)
        vbox.setAlignment(Qt.AlignTop)

        # --- כותרת ---
        self.title_label = QLabel(f"✈ {self.plane.Name}")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: 600;
                color: #1F2D3D;
            }
        """
        )
        vbox.addWidget(self.title_label)

        # --- קו חוצץ ---
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #D5E7EE; margin: 4px 0 8px 0;")
        vbox.addWidget(line)

        # --- תמונה ---
        self.img_label = QLabel()
        self.img_label.setFixedSize(QSize(360, 210))
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet(
            """
            QLabel {
                border-radius: 12px;
                background-color: #F9FCFD;
            }
        """
        )

        pix = self.cache.cache.get(self.plane.Picture)
        if not pix and self.plane.Picture:
            try:
                if self.plane.Picture.startswith("http"):
                    r = requests.get(self.plane.Picture, timeout=5)
                    if r.status_code == 200:
                        pix = QPixmap()
                        pix.loadFromData(BytesIO(r.content).read())
                else:
                    pix = QPixmap(self.plane.Picture)
            except Exception:
                pix = None

        if pix and not pix.isNull():
            self.img_label.setPixmap(
                pix.scaled(self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.img_label.setPixmap(QPixmap("frontend/assets/icons/plane.svg"))

        vbox.addWidget(self.img_label, alignment=Qt.AlignCenter)

        # --- מידע ---
        total = self.plane.NumOfSeats1 + self.plane.NumOfSeats2 + self.plane.NumOfSeats3
        self.info_label = QLabel(
            f"<b>Manufacturer:</b> {self.plane.MadeBy}<br>"
            f"<b>Year:</b> {self.plane.Year}<br>"
            f"<b>Total Seats:</b> {total}"
        )
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet(
            """
            QLabel {
                color: #2E4B5B;
                font-size: 14px;
                margin-top: 10px;
            }
        """
        )
        vbox.addWidget(self.info_label)

        # --- כפתור עריכה ---
        edit_btn = QPushButton("✏ Edit Plane")
        edit_btn.setFixedWidth(200)
        edit_btn.clicked.connect(lambda: self.presenter.open_edit_plane(self.plane))
        vbox.addWidget(edit_btn, alignment=Qt.AlignCenter)

        # --- עיצוב כללי לכפתור ---
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #4BA3C7;
                color: white;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #3A94B8; }
        """
        )

    def refresh_data(self, updated_plane):
        """מרעננת את פרטי המטוס בחלון הקיים"""
        self.plane = updated_plane
        self.title_label.setText(f"✈ {self.plane.Name}")
        total = self.plane.NumOfSeats1 + self.plane.NumOfSeats2 + self.plane.NumOfSeats3
        self.info_label.setText(
            f"<b>Manufacturer:</b> {self.plane.MadeBy}<br>"
            f"<b>Year:</b> {self.plane.Year}<br>"
            f"<b>Total Seats:</b> {total}"
        )

        # ריענון תמונה
        if self.plane.Picture:
            try:
                r = requests.get(self.plane.Picture, timeout=3)
                if r.status_code == 200:
                    pix = QPixmap()
                    pix.loadFromData(r.content)
                    scaled = pix.scaled(
                        self.img_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                    self.img_label.setPixmap(scaled)
            except Exception:
                pass
