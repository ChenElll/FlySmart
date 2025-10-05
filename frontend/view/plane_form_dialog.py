from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Qt


class PlaneFormDialog(QDialog):
    def __init__(self, presenter, mode="add", plane=None):
        """
        mode: "add" or "edit"
        plane: optional PlaneEntity object (for edit mode)
        """
        super().__init__()
        self.presenter = presenter
        self.mode = mode
        self.plane = plane

        # Window setup
        self.setWindowTitle("✈ Add New Plane" if mode == "add" else "✈ Update Plane")
        self.setFixedWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #f5f5f5;
            }
            QLineEdit {
                background-color: #404040;
                color: #fff;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton {
                background-color: #00bfa5;
                color: black;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1de9b6;
            }
        """)

        # === Form Fields ===
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.year_input = QLineEdit()
        self.madeby_input = QLineEdit()
        self.picture_input = QLineEdit()
        self.seats1_input = QLineEdit()
        self.seats2_input = QLineEdit()
        self.seats3_input = QLineEdit()

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Year:", self.year_input)
        form_layout.addRow("Made By:", self.madeby_input)
        form_layout.addRow("Picture URL:", self.picture_input)
        form_layout.addRow("Seats1:", self.seats1_input)
        form_layout.addRow("Seats2:", self.seats2_input)
        form_layout.addRow("Seats3:", self.seats3_input)

        # אם זה מצב עריכה – נטעין את הנתונים הקיימים
        if self.mode == "edit" and plane:
            self.name_input.setText(plane.Name)
            self.year_input.setText(str(plane.Year))
            self.madeby_input.setText(plane.MadeBy)
            self.picture_input.setText(plane.Picture or "")
            self.seats1_input.setText(str(plane.NumOfSeats1))
            self.seats2_input.setText(str(plane.NumOfSeats2))
            self.seats3_input.setText(str(plane.NumOfSeats3))

        # === Buttons ===
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save")
        cancel_btn = QPushButton("✖ Cancel")

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        save_btn.clicked.connect(self.save_plane)
        cancel_btn.clicked.connect(self.close)

        # === Main Layout ===
        layout = QVBoxLayout()
        title = QLabel("Add New Plane" if mode == "add" else "Edit Plane Details")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #fdd835; font-weight: bold; font-size: 16px;")

        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    # ---------------- SAVE ----------------
    def save_plane(self):
        """Collect data and call presenter"""
        try:
            name = self.name_input.text().strip()
            year = int(self.year_input.text().strip())
            made_by = self.madeby_input.text().strip()
            picture = self.picture_input.text().strip()
            seats1 = int(self.seats1_input.text().strip())
            seats2 = int(self.seats2_input.text().strip())
            seats3 = int(self.seats3_input.text().strip())

            if not name or not made_by:
                QMessageBox.warning(self, "Invalid input", "Please fill all required fields.")
                return

            if self.mode == "add":
                self.presenter.add_plane(name, year, made_by, picture, seats1, seats2, seats3)
            else:
                self.presenter.update_plane(self.plane.PlaneId, name, year, made_by, picture, seats1, seats2, seats3)

            self.accept()

        except ValueError:
            QMessageBox.warning(self, "Invalid input", "Please enter valid numbers for year and seats.")
