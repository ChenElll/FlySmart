from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QIntValidator
import requests
import datetime


class PlaneFormDialog(QDialog):
    """חלון עריכה/הוספה של מטוס — כולל ולידציה, מחיקה ותצוגת תמונה"""
    def __init__(self, presenter, mode="add", plane=None):
        super().__init__()
        self.presenter = presenter
        self.mode = mode
        self.plane = plane

        self.setWindowTitle("✈ Edit Plane" if mode == "edit" else "✈ Add Plane")
        self.setWindowIcon(QIcon("frontend/assets/icons/airplane.svg"))
        self.setFixedWidth(520)
        self.setStyleSheet("""
            QDialog {
                background-color: #F7FBFD;
                border-radius: 12px;
            }
            QLabel {
                color: #1A2C3A;
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #C3D8E3;
                border-radius: 8px;
                padding: 6px 8px;
                font-size: 14px;
                background: white;
            }
            QPushButton {
                font-weight: 600;
                border-radius: 10px;
                padding: 8px 18px;
            }
            QPushButton#save {
                background-color: #7AB9E0;
                color: white;
            }
            QPushButton#save:hover {
                background-color: #67A8D4;
            }
            QPushButton#delete {
                background-color: #F3C4C4;
                color: #333;
            }
            QPushButton#delete:hover {
                background-color: #E89C9C;
            }
            QPushButton#cancel {
                background-color: #E2EFF4;
                color: #333;
            }
            QPushButton#cancel:hover {
                background-color: #D0E4EB;
            }
        """)

        self._build_ui()
        if self.mode == "edit" and self.plane:
            self._populate_fields()

    # ------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # כותרת עליונה
        title = QLabel("✈ Edit Plane" if self.mode == "edit" else "✈ Add Plane")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #1A2C3A;")
        layout.addWidget(title)

        # שדות טופס
        self.inputs = {}
        fields = [
            ("Name", "Name:"),
            ("Year", "Year:"),
            ("MadeBy", "MadeBy:"),
            ("Picture", "Image URL (optional):"),
            ("NumOfSeats1", "Seats Class 1:"),
            ("NumOfSeats2", "Seats Class 2:"),
            ("NumOfSeats3", "Seats Class 3:")
        ]

        for key, label_text in fields:
            row = QHBoxLayout()
            row.setSpacing(10)

            label = QLabel(label_text)
            label.setStyleSheet("font-weight: 600; min-width: 140px;")
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            field = QLineEdit()
            field.setPlaceholderText(f"Enter {key}")
            field.setFixedHeight(32)
            field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            if "Seats" in key or key == "Year":
                field.setValidator(QIntValidator(0, 9999))

            row.addWidget(label)
            row.addWidget(field)
            layout.addLayout(row)
            self.inputs[key] = field

        # תצוגת תמונה
        self.preview_label = QLabel("No image preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(400, 220)
        self.preview_label.setStyleSheet("""
            border: 2px dashed #C3D8E3;
            border-radius: 12px;
            color: #A1B6C4;
            background-color: #FDFEFE;
        """)
        layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)

        # שינוי אוטומטי של התמונה כאשר URL משתנה
        self.inputs["Picture"].textChanged.connect(self._update_preview)

        # כפתורים
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        save_btn = QPushButton("💾 Save")
        save_btn.setObjectName("save")
        save_btn.clicked.connect(self._save_plane)

        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setObjectName("delete")
        delete_btn.clicked.connect(self._delete_plane)

        cancel_btn = QPushButton("✖ Cancel")
        cancel_btn.setObjectName("cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(save_btn)
        if self.mode == "edit":
            btn_box.addWidget(delete_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)

    # ------------------------------------------------------------
    def _collect_form_data(self):
        """אוספת נתונים מהשדות לטובת שמירה/עדכון"""
        return {
            "Name": self.inputs["Name"].text().strip(),
            "Year": int(self.inputs["Year"].text().strip() or 0),
            "MadeBy": self.inputs["MadeBy"].text().strip(),
            "Picture": self.inputs["Picture"].text().strip(),
            "NumOfSeats1": int(self.inputs["NumOfSeats1"].text().strip() or 0),
            "NumOfSeats2": int(self.inputs["NumOfSeats2"].text().strip() or 0),
            "NumOfSeats3": int(self.inputs["NumOfSeats3"].text().strip() or 0),
        }

    # ------------------------------------------------------------
    def _validate_form(self, data):
        """בודקת שהנתונים שהוזנו תקינים"""
        current_year = datetime.datetime.now().year

        if not data["Name"]:
            return False, "Please enter a plane name."
        if data["Year"] <= 0 or data["Year"] > current_year + 1:
            return False, f"Year must be between 1 and {current_year + 1}."
        if not data["MadeBy"]:
            return False, "Please enter manufacturer name."
        if all(v == 0 for v in (data["NumOfSeats1"], data["NumOfSeats2"], data["NumOfSeats3"])):
            return False, "Please enter at least one seat class count."
        return True, ""

    # ------------------------------------------------------------
    def _populate_fields(self):
        """ממלא את השדות בנתונים של המטוס הנבחר"""
        for key in self.inputs:
            value = getattr(self.plane, key, "")
            self.inputs[key].setText(str(value) if value is not None else "")
        self._update_preview()

    # ------------------------------------------------------------
    def _update_preview(self):
        """טוען תמונה מתוקנת ללא גלישה"""
        url = self.inputs["Picture"].text().strip()
        if not url:
            self.preview_label.setText("No image preview")
            self.preview_label.setPixmap(QPixmap())
            return

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                pix = QPixmap()
                pix.loadFromData(response.content)
                scaled = pix.scaled(
                    self.preview_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)
                self.preview_label.setText("")
            else:
                self.preview_label.setText("Failed to load image")
        except Exception:
            self.preview_label.setText("Invalid URL or connection error")

    # ------------------------------------------------------------
    def _save_plane(self):
        """שומר שינויים במטוס בצורה נקייה ועם בדיקה מוקדמת"""
        try:
            data = self._collect_form_data()
            valid, err = self._validate_form(data)
            if not valid:
                QMessageBox.warning(self, "Invalid Data", err)
                return

            success, msg = self.presenter.save_plane(self.mode, data, self.plane)
            if success:
                if hasattr(self.presenter, "load_planes"):
                    self.presenter.load_planes()
                self.accept()
            elif msg:
                QMessageBox.critical(self, "Error", msg)
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", str(e))

    # ------------------------------------------------------------
    def _delete_plane(self):
        """מאשר ומבצע מחיקת מטוס"""
        if not self.plane:
            QMessageBox.warning(self, "Error", "No plane to delete.")
            return

        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{self.plane.Name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            success, msg = self.presenter.delete_plane(self.plane.PlaneId)
            if success:
                self.accept()
            if msg:
                QMessageBox.information(self, "Result", msg)
