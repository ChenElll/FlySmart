from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QPixmap, QIntValidator, QColor, QLinearGradient, QPalette, QBrush
import requests


class PlaneFormDialog(QDialog):
    """חלון עריכה/הוספה של מטוס — כולל מחיקה וסגירת חלונות"""
    def __init__(self, presenter, mode="add", plane=None):
        super().__init__()
        self.presenter = presenter
        self.mode = mode
        self.plane = plane

        self.setWindowTitle("✈ Edit Plane" if mode == "edit" else "➕ Add New Plane")
        self.setModal(True)
        self.setFixedSize(520, 720)
        self._build_ui()

    # ------------------------------------------------------------
    def _build_ui(self):
        # רקע עם גרדיאנט תכלת
        palette = QPalette()
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor("#F8FBFD"))
        grad.setColorAt(1, QColor("#EAF4F9"))
        palette.setBrush(QPalette.Window, QBrush(grad))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # כרטיס לבן
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 18px;
                border: 1px solid #DCE8EE;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 20, 30, 20)
        outer.addWidget(container, alignment=Qt.AlignCenter)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(14)

        # --- כותרת ---
        title = QLabel("✈ Edit Plane" if self.mode == "edit" else "➕ Add New Plane")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: 700;
                color: #2A5268;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # קו מפריד
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #D5E7EE;")
        layout.addWidget(line)

        # --- שדות קלט ---
        self.name_input = self._add_field(layout, "✈ Name:")
        self.year_input = self._add_field(layout, "Year:", QIntValidator(1900, 2100))
        self.made_by_input = self._add_field(layout, "Manufacturer:")
        self.picture_input = self._add_field(layout, "Image URL (optional):")
        self.seats1_input = self._add_field(layout, "Seats Class 1:", QIntValidator(0, 999))
        self.seats2_input = self._add_field(layout, "Seats Class 2:", QIntValidator(0, 999))
        self.seats3_input = self._add_field(layout, "Seats Class 3:", QIntValidator(0, 999))

        # --- תצוגת תמונה ---
        self.preview_label = QLabel("No image preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(400, 220)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #C6E2EE;
                border-radius: 12px;
                background-color: #F8FBFD;
                color: #7AA4B7;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)

        # טעינה אוטומטית של preview אחרי השהייה
        self._url_timer = QTimer()
        self._url_timer.setSingleShot(True)
        self._url_timer.timeout.connect(self._load_preview_image)
        self.picture_input.textChanged.connect(lambda: self._url_timer.start(500))

        if self.mode == "edit" and self.plane:
            self._load_plane_data()
            if self.plane.Picture:
                self._display_image(self.plane.Picture)

        layout.addItem(QSpacerItem(10, 15, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addSpacing(10)

        # --- כפתורים ---
        btn_box = QHBoxLayout()
        btn_box.setSpacing(14)

        save_btn = QPushButton("💾 Save")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self._on_save)

        delete_btn = QPushButton("🗑 Delete")
        delete_btn.setObjectName("deleteBtn")
        delete_btn.clicked.connect(self._on_delete)

        cancel_btn = QPushButton("✖ Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)

        btn_box.addStretch()
        btn_box.addWidget(save_btn)
        if self.mode == "edit":
            btn_box.addWidget(delete_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)

        # --- עיצוב ---
        self.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 1px solid #D5E7EE;
                padding: 6px 4px;
                background-color: #FAFCFD;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-bottom: 1px solid #4BA3C7;
                background-color: #FFFFFF;
            }
            QPushButton {
                min-width: 150px;
                min-height: 36px;
                border-radius: 10px;
                font-weight: 600;
                padding: 8px 18px;
                font-size: 14px;
            }
            QPushButton#saveBtn {
                background-color: #4BA3C7;
                color: white;
            }
            QPushButton#saveBtn:hover { background-color: #3A94B8; }
            QPushButton#cancelBtn {
                background-color: #E8F4F8;
                color: #4BA3C7;
            }
            QPushButton#cancelBtn:hover { background-color: #D7EEF3; }
            QPushButton#deleteBtn {
                background-color: #FAD4D4;
                color: #A60000;
            }
            QPushButton#deleteBtn:hover {
                background-color: #F8BABA;
            }
        """)

    # ------------------------------------------------------------
    def _add_field(self, layout, label_text, validator=None):
        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-weight: 500; color: #244F63;")
        field = QLineEdit()
        if validator:
            field.setValidator(validator)
        layout.addWidget(lbl)
        layout.addWidget(field)
        return field

    # ------------------------------------------------------------
    def _load_preview_image(self):
        """טעינת תצוגת תמונה (ללא threads)"""
        url = self.picture_input.text().strip()
        if not url:
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("No Image")
            return

        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                pix = QPixmap()
                pix.loadFromData(r.content)
                if not pix.isNull():
                    scaled = pix.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.preview_label.setPixmap(scaled)
                    self.preview_label.setText("")
                    return
        except Exception:
            pass

        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText("❌ Failed to load image")

    def _display_image(self, url):
        """טעינת תמונה מתוך הנתון הקיים של המטוס"""
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                pix = QPixmap()
                pix.loadFromData(r.content)
                scaled = pix.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_label.setPixmap(scaled)
        except Exception:
            self.preview_label.setText("❌ Failed to load image")

    # ------------------------------------------------------------
    def _load_plane_data(self):
        """ממלא את נתוני המטוס הקיים בשדות"""
        self.name_input.setText(self.plane.Name)
        self.year_input.setText(str(self.plane.Year))
        self.made_by_input.setText(self.plane.MadeBy)
        self.picture_input.setText(self.plane.Picture or "")
        self.seats1_input.setText(str(self.plane.NumOfSeats1))
        self.seats2_input.setText(str(self.plane.NumOfSeats2))
        self.seats3_input.setText(str(self.plane.NumOfSeats3))

    # ------------------------------------------------------------
    def _on_save(self):
        """שמירת הנתונים (הוספה/עדכון)"""
        name = self.name_input.text().strip()
        year = self.year_input.text().strip()
        made_by = self.made_by_input.text().strip()
        picture = self.picture_input.text().strip() or None
        s1 = self.seats1_input.text().strip() or "0"
        s2 = self.seats2_input.text().strip() or "0"
        s3 = self.seats3_input.text().strip() or "0"

        if not name or not year or not made_by:
            QMessageBox.warning(self, "Missing Data", "Please fill all required fields.")
            return

        try:
            year = int(year)
            s1, s2, s3 = int(s1), int(s2), int(s3)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Numeric fields must contain numbers.")
            return

        if self.mode == "edit" and self.plane:
            self.presenter.update_plane(self.plane.PlaneId, name, year, made_by, picture, s1, s2, s3)
        else:
            self.presenter.add_plane(name, year, made_by, picture, s1, s2, s3)

        self.accept()

    # ------------------------------------------------------------
    def _on_delete(self):
        """מאשר ומוחק את המטוס הנוכחי וסוגר את כל החלונות הקטנים"""
        if not self.plane:
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{self.plane.Name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            try:
                # מוחק מה־DB
                self.presenter.delete_plane(self.plane.PlaneId)

                # ✨ סגירת חלון פרטים אם פתוח
                if hasattr(self.presenter.view, "active_details_dialog") and self.presenter.view.active_details_dialog:
                    try:
                        self.presenter.view.active_details_dialog.close()
                        self.presenter.view.active_details_dialog = None
                    except Exception:
                        pass

                # ✨ רענון רשימת המטוסים הראשית
                self.presenter.load_planes()

                # ✨ סגירת חלון העריכה עצמו
                self.accept()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete plane: {e}")

    # ------------------------------------------------------------
    def keyPressEvent(self, event):
        """מאפשר שמירה ע"י לחיצה על Enter"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._on_save()
        else:
            super().keyPressEvent(event)
