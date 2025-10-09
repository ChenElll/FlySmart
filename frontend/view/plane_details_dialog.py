from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
import requests


class PlaneDetailsDialog(QDialog):
    """חלון הצגת פרטי מטוס — תצוגה בלבד, עם כפתור עריכה בלבד"""
    def __init__(self, parent, plane, cache_manager, presenter):
        super().__init__(parent)
        self.plane = plane
        self.cache = cache_manager
        self.presenter = presenter

        self.setWindowTitle(f"Plane Details – {plane.Name}")
        self.setWindowIcon(QIcon("frontend/assets/icons/airplane.svg"))
        self.setMinimumWidth(560)
        self.setStyleSheet("""
            QDialog {
                background-color: #F7FBFD;
                border-radius: 12px;
            }
            QLabel {
                color: #1A2C3A;
                font-size: 14px;
            }
            QLabel#title {
                font-size: 20px;
                font-weight: 700;
                color: #1A2C3A;
            }
            QLabel#subtitle {
                font-size: 13px;
                color: #5A6D78;
            }
            QPushButton {
                font-weight: 600;
                border-radius: 10px;
                padding: 8px 18px;
            }
            QPushButton#edit {
                background-color: #7AB9E0;
                color: white;
            }
            QPushButton#edit:hover { background-color: #67A8D4; }
            QFrame#container {
                background: white;
                border-radius: 14px;
                border: 1px solid #D8E8EE;
            }
        """)

        self._build_ui()

    # ------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # כותרת
        title = QLabel(f"✈ {self.plane.Name}")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # תיבה מרכזית עם פרטים
        frame = QFrame()
        frame.setObjectName("container")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(25, 25, 25, 25)
        frame_layout.setSpacing(14)

        # תמונה
        self.img_label = QLabel()
        self.img_label.setFixedSize(420, 220)
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("""
            border: 2px dashed #C3D8E3;
            border-radius: 12px;
            color: #A1B6C4;
            background-color: #FDFEFE;
        """)
        frame_layout.addWidget(self.img_label, alignment=Qt.AlignCenter)
        self._load_image()

        # מידע טקסטואלי
        info_texts = [
            ("ID:", str(self.plane.PlaneId)),
            ("Manufacturer:", self.plane.MadeBy),
            ("Year:", str(self.plane.Year)),
            ("Total Seats:", str(self.plane.NumOfSeats1 + self.plane.NumOfSeats2 + self.plane.NumOfSeats3)),
            ("Image URL:", self.plane.Picture or "None"),
        ]

        for label_text, value_text in info_texts:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: 600; min-width: 160px; color: #1A2C3A;")
            val = QLabel(value_text)
            val.setStyleSheet("color: #3C4E56;")
            row.addWidget(lbl)
            row.addWidget(val)
            frame_layout.addLayout(row)

        layout.addWidget(frame)

        # כפתור עריכה בלבד
        edit_btn = QPushButton("Edit Plane")
        edit_btn.setObjectName("edit")
        edit_btn.setFixedWidth(180)
        edit_btn.clicked.connect(self._edit_plane)
        layout.addWidget(edit_btn, alignment=Qt.AlignCenter)

    # ------------------------------------------------------------
    def _load_image(self):
        """טעינת תמונה עם fallback"""
        url = self.plane.Picture
        pix = QPixmap("frontend/assets/icons/airplane.svg")

        try:
            if url and url.startswith("http"):
                r = requests.get(url, timeout=3)
                if r.status_code == 200:
                    p = QPixmap()
                    p.loadFromData(r.content)
                    if not p.isNull():
                        pix = p
        except Exception:
            pass

        scaled = pix.scaled(self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img_label.setPixmap(scaled)

    # ------------------------------------------------------------
    def _edit_plane(self):
        """פותח את חלון העריכה מתוך דיאלוג הפרטים"""
        try:
            self.presenter.open_edit_plane(self.plane)
            # אחרי עריכה — נרענן את התצוגה
            refreshed = self.presenter.get_plane_by_id(self.plane.PlaneId)
            if refreshed:
                self.plane = refreshed
                self._rebuild_after_update()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open edit dialog:\n{e}")

    def _rebuild_after_update(self):
        """מרענן את תוכן הדיאלוג אחרי עדכון"""
        self.layout().itemAt(0).widget().setText(f"✈ {self.plane.Name}")
        self._load_image()
