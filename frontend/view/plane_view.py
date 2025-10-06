from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QFrame,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import requests



class PlaneView(QMainWindow):
    def __init__(self, presenter):
        super().__init__()
        self.presenter = presenter

        # Load external stylesheet
        with open("frontend/assets/style.qss", "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        # Window icon
        self.setWindowIcon(QIcon("frontend/assets/plane_icon.ico"))

        # === Main Window Settings ===
        self.setWindowTitle("FlySmart - Plane Management")
        self.resize(1200, 700)

        # === Title + Refresh Button ===
        title = QLabel("✈ Plane Management Dashboard")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)

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

        # === Left Panel (placeholder for plane card) ===
        self.detail_container = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_container)
        self.detail_layout.setAlignment(Qt.AlignTop)
        self.detail_container.setMinimumWidth(400)

        # === Right Panel (List of Planes) ===
        self.right_list = QListWidget()
        self.right_list.setMaximumWidth(300)
        self.right_list.setSpacing(4)

        # === Content Layout ===
        content_layout = QHBoxLayout()
        content_layout.addWidget(self.right_list)  # עכשיו הרשימה בצד שמאל
        content_layout.addStretch()
        content_layout.addWidget(self.detail_container)  # הכרטיס עובר לימין

        # === Main Layout ===
        main_layout = QVBoxLayout()
        main_layout.addLayout(title_layout)
        main_layout.addLayout(content_layout)

        # === Central Widget ===
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # === SIGNAL CONNECTIONS ===
        self.right_list.itemClicked.connect(self.on_plane_selected)

    # ------------------- Display Logic -------------------

    def show_planes(self, planes):
        """מציג שמות מטוסים ברשימה הימנית"""
        self.right_list.clear()
        for plane in planes:
            item = QListWidgetItem(plane.Name)
            item.setData(Qt.UserRole, plane.PlaneId)
            self.right_list.addItem(item)

    def show_plane_card(self, plane):
        """מציג כרטיס מידע יפה בצד שמאל במקום panel ישן"""
        # ננקה תוכן קודם
        for i in reversed(range(self.detail_layout.count())):
            widget = self.detail_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        card = QFrame()
        card.setObjectName("PlaneCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignTop)

        card.setStyleSheet("""
            QFrame#PlaneCard {
                background-color: #2b2b2b;
                border-radius: 10px;
                border: 1px solid #444;
                padding: 15px;
            }
            QLabel#PlaneCardTitle {
                color: #00bfa5;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 8px;
            }
        """)

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
                else:
                    print(f"⚠ Image not found (status {response.status_code})")
            except Exception as e:
                print(f"⚠ Failed to load image: {e}")

        # === כותרת המטוס ===
        title = QLabel(f"✈ {plane.Name}")
        title.setObjectName("PlaneCardTitle")
        title.setAlignment(Qt.AlignCenter)

        # === פרטי המטוס ===
        info = QLabel(
            f"<b>Manufacturer:</b> {plane.MadeBy}<br>"
            f"<b>Year:</b> {plane.Year}<br>"
            f"<b>Seats:</b> {plane.NumOfSeats1 + plane.NumOfSeats2 + plane.NumOfSeats3}"
        )
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)

        # === כפתור עריכה ===
        edit_btn = QPushButton("✏ Edit Details")
        edit_btn.clicked.connect(lambda: self.presenter.open_edit_plane(plane))

        # הוספה לכרטיס
        card_layout.addWidget(title)
        card_layout.addWidget(info)
        card_layout.addWidget(edit_btn, alignment=Qt.AlignCenter)
        card_layout.addStretch()

        self.detail_layout.addWidget(card)

    def on_plane_selected(self, item):
        plane_id = item.data(Qt.UserRole)
        if not self.presenter:
            return
        plane = self.presenter.show_plane_details(plane_id)
        if plane:
            self.show_plane_card(plane)

    def show_error(self, message: str):
        QMessageBox.critical(self, "Error", message)
