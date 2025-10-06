from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QFrame, QLineEdit, QComboBox
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
import requests


class PlaneView(QMainWindow):
    def __init__(self, presenter):
        super().__init__()
        self.presenter = presenter

        # === Load stylesheet ===
        with open("frontend/assets/style.qss", "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        self.setWindowIcon(QIcon("frontend/assets/plane_icon.ico"))
        self.setWindowTitle("FlySmart - Plane Management")
        self.resize(1200, 700)

        # === Title + Buttons ===
        title = QLabel("✈ Plane Management Dashboard")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)

        add_btn = QPushButton("➕")
        add_btn.setToolTip("Add new plane")
        add_btn.setFixedSize(32, 32)
        add_btn.clicked.connect(self.presenter.open_add_plane)

        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Refresh plane list")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.clicked.connect(self.presenter.load_planes)

        title_layout = QHBoxLayout()
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(add_btn)
        title_layout.addWidget(refresh_btn)

        # === LEFT: Plane List + Search ===
        self.right_list = QListWidget()
        self.right_list.setSpacing(4)
        self.right_list.setMaximumWidth(320)

        # Search & Filters
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search by name...")
        self.search_bar.textChanged.connect(self.apply_filters)

        self.manufacturer_filter = QComboBox()
        self.manufacturer_filter.addItems([
            "All Manufacturers", "Boeing", "Airbus", "Embraer", "Bombardier", "McDonnell Douglas"
        ])
        self.manufacturer_filter.currentIndexChanged.connect(self.apply_filters)

        self.seats_filter = QComboBox()
        self.seats_filter.addItems(["All Sizes", "Small (≤100)", "Medium (101–250)", "Large (>250)"])
        self.seats_filter.currentIndexChanged.connect(self.apply_filters)

        reset_btn = QPushButton("♻ Reset")
        reset_btn.setFixedWidth(80)
        reset_btn.clicked.connect(self.reset_filters)

        filters_layout = QHBoxLayout()
        filters_layout.addWidget(self.search_bar)
        filters_layout.addWidget(self.manufacturer_filter)
        filters_layout.addWidget(self.seats_filter)
        filters_layout.addWidget(reset_btn)

        left_panel = QVBoxLayout()
        left_panel.addLayout(filters_layout)
        left_panel.addWidget(self.right_list)

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(350)

        # === RIGHT: Plane Details Card ===
        self.detail_container = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_container)
        self.detail_layout.setAlignment(Qt.AlignTop)
        self.detail_container.setMinimumWidth(400)

        # === Combine Layouts ===
        content_layout = QHBoxLayout()
        content_layout.addWidget(left_widget)
        content_layout.addWidget(self.detail_container)

        main_layout = QVBoxLayout()
        main_layout.addLayout(title_layout)
        main_layout.addLayout(content_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # === SIGNAL CONNECTIONS ===
        self.right_list.itemClicked.connect(self.on_plane_selected)

    # ------------------- Display Logic -------------------

    def show_planes(self, planes):
        """מציג את רשימת המטוסים ומאפס את הסינון"""
        self.planes = planes
        self.apply_filters()

    def apply_filters(self):
        """מסנן את רשימת המטוסים לפי שם, יצרן, ומספר מושבים"""
        if not hasattr(self, "planes"):
            return

        search_text = self.search_bar.text().lower()
        manufacturer = self.manufacturer_filter.currentText()
        seat_filter = self.seats_filter.currentText()

        self.right_list.clear()

        for plane in self.planes:
            total_seats = plane.NumOfSeats1 + plane.NumOfSeats2 + plane.NumOfSeats3
            if (
                search_text in plane.Name.lower()
                and (manufacturer == "All Manufacturers" or plane.MadeBy == manufacturer)
                and (
                    seat_filter == "All Sizes"
                    or (seat_filter == "Small (≤100)" and total_seats <= 100)
                    or (seat_filter == "Medium (101–250)" and 101 <= total_seats <= 250)
                    or (seat_filter == "Large (>250)" and total_seats > 250)
                )
            ):
                item = QListWidgetItem(plane.Name)
                item.setData(Qt.UserRole, plane.PlaneId)
                self.right_list.addItem(item)

    def reset_filters(self):
        self.search_bar.clear()
        self.manufacturer_filter.setCurrentIndex(0)
        self.seats_filter.setCurrentIndex(0)
        self.apply_filters()

    def on_plane_selected(self, item):
        plane_id = item.data(Qt.UserRole)
        if not self.presenter:
            return
        plane = self.presenter.get_plane_by_id(plane_id)
        if plane:
            self.show_plane_card(plane)

    def show_plane_card(self, plane):
        """מציג כרטיס מידע יפה בצד ימין"""
        for i in reversed(range(self.detail_layout.count())):
            widget = self.detail_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        card = QFrame()
        card.setObjectName("PlaneCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignTop)

        # === תמונה של המטוס ===
        if plane.Picture:
            try:
                response = requests.get(plane.Picture, timeout=3)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    image_label = QLabel()
                    image_label.setPixmap(pixmap.scaledToWidth(350, Qt.SmoothTransformation))
                    image_label.setAlignment(Qt.AlignCenter)
                    card_layout.addWidget(image_label)
            except Exception as e:
                print(f"⚠ Failed to load image: {e}")

        title = QLabel(f"✈ {plane.Name}")
        title.setObjectName("PlaneCardTitle")
        title.setAlignment(Qt.AlignCenter)

        info = QLabel(
            f"<b>Manufacturer:</b> {plane.MadeBy}<br>"
            f"<b>Year:</b> {plane.Year}<br>"
            f"<b>Seats:</b> {plane.NumOfSeats1 + plane.NumOfSeats2 + plane.NumOfSeats3}"
        )
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)

        edit_btn = QPushButton("✏ Edit Details")
        edit_btn.clicked.connect(lambda: self.presenter.open_edit_plane(plane))

        card_layout.addWidget(title)
        card_layout.addWidget(info)
        card_layout.addWidget(edit_btn, alignment=Qt.AlignCenter)
        card_layout.addStretch()
        self.detail_layout.addWidget(card)

    def show_error(self, message: str):
        QMessageBox.critical(self, "Error", message)
