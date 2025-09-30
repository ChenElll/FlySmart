from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QFormLayout, QLineEdit, QListWidget, QListWidgetItem
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt


class PlaneView(QMainWindow):
    def __init__(self, presenter=None):
        super().__init__()
        self.presenter = presenter

        # Load external stylesheet
        with open("frontend/assets/style.qss", "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        # אייקון החלון
        self.setWindowIcon(QIcon("frontend/assets/plane_icon.ico"))

        # === Main Window Settings ===
        self.setWindowTitle("FlySmart - Plane Management")
        self.resize(1200, 700)

        # === Title ===
        title = QLabel("✈ Plane Management Dashboard")
        title.setObjectName("TitleLabel") 
        title.setAlignment(Qt.AlignCenter)

        # === CRUD Buttons ===
        btn_add = QPushButton("➕ Add")
        btn_update = QPushButton("✏ Update")
        btn_delete = QPushButton("🗑 Delete")
        btn_refresh = QPushButton("🔄 Refresh")

        button_layout = QHBoxLayout()
        button_layout.addWidget(btn_add)
        button_layout.addWidget(btn_update)
        button_layout.addWidget(btn_delete)
        button_layout.addStretch()
        button_layout.addWidget(btn_refresh)


        # === Left Panel (Details) ===
        self.detail_panel = QWidget()
        detail_layout = QFormLayout()

        self.id_field = QLineEdit()
        self.name_field = QLineEdit()
        self.year_field = QLineEdit()
        self.madeby_field = QLineEdit()
        self.seats1_field = QLineEdit()
        self.seats2_field = QLineEdit()
        self.seats3_field = QLineEdit()

        for widget in [
            self.id_field, self.name_field, self.year_field,
            self.madeby_field, self.seats1_field, self.seats2_field, self.seats3_field
        ]:
            widget.setReadOnly(True)

        detail_layout.addRow("ID:", self.id_field)
        detail_layout.addRow("Name:", self.name_field)
        detail_layout.addRow("Year:", self.year_field)
        detail_layout.addRow("Made By:", self.madeby_field)
        detail_layout.addRow("Seats1:", self.seats1_field)
        detail_layout.addRow("Seats2:", self.seats2_field)
        detail_layout.addRow("Seats3:", self.seats3_field)

        self.detail_panel.setLayout(detail_layout)

        # === Layouts ===
        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addLayout(button_layout)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.detail_panel)   # פרטים בצד שמאל
        content_layout.addStretch()

        main_layout.addLayout(content_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


        # === Right Panel (List of Planes) ===
        self.right_list = QListWidget()
        self.right_list.setMaximumWidth(300)
        self.right_list.setSpacing(4)  # רווחים בין פריטים

        content_layout.addWidget(self.right_list)

    def show_planes(self, planes):

        """מציג שמות מטוסים בטבלה הימנית"""
        self.right_list.clear()
        for plane in planes:
            item = QListWidgetItem(plane.Name)
            self.right_list.addItem(item)

    def show_plane_details(self, plane):
        """מציג פרטים בפאנל השמאלי"""
        self.id_field.setText(str(plane.PlaneId))
        self.name_field.setText(plane.Name)
        self.year_field.setText(str(plane.Year))
        self.madeby_field.setText(plane.MadeBy)
        self.seats1_field.setText(str(plane.NumOfSeats1))
        self.seats2_field.setText(str(plane.NumOfSeats2))
        self.seats3_field.setText(str(plane.NumOfSeats3))

    def show_error(self, message: str):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", message)
