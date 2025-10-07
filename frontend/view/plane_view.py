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
    QLineEdit,
    QComboBox,
    QStyledItemDelegate,
    QSizePolicy,
    QDockWidget,
)
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtCore import Qt, QSize, QRect
import requests
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtCore import QAbstractAnimation




class PlaneIconDelegate(QStyledItemDelegate):
    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        self.icon = QIcon(icon_path)

    def paint(self, painter, option, index):
        # Draw the default item (text)
        super().paint(painter, option, index)
        # Draw the icon at the right edge
        icon_size = 24
        rect = option.rect
        icon_rect = QRect(
            rect.right() - icon_size - 12,
            rect.top() + (rect.height() - icon_size) // 2,
            icon_size,
            icon_size,
        )
        self.icon.paint(painter, icon_rect, Qt.AlignCenter)

    def sizeHint(self, option, index):
        return QSize(300, 48)


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

        # === LEFT: Plane List + Search ===
        self.right_list = QListWidget()
        self.right_list.setSpacing(4)
        self.right_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search by name...")
        self.search_bar.textChanged.connect(self.apply_filters)

        self.manufacturer_filter = QComboBox()
        self.manufacturer_filter.addItems(
            [
                "All Manufacturers",
                "Boeing",
                "Airbus",
                "Embraer",
                "Bombardier",
                "McDonnell Douglas",
            ]
        )
        self.manufacturer_filter.currentIndexChanged.connect(self.apply_filters)

        self.seats_filter = QComboBox()
        self.seats_filter.addItems(
            ["All Sizes", "Small (≤100)", "Medium (101–250)", "Large (>250)"]
        )
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
        left_panel.addWidget(self.right_list, stretch=1)

        left_widget_content = QWidget()
        left_widget_content.setLayout(left_panel)

        self.left_dock = QDockWidget("", self)
        self.left_dock.setWidget(left_widget_content)
        self.left_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.left_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.left_dock.setFixedWidth(380)
        self.left_dock.hide()

        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        # === כפתור לפתיחת הרשימה ===
        self.menu_btn = QPushButton()
        self.menu_btn.setIcon(QIcon("frontend/assets/icons/menu.svg"))
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.setObjectName("RoundIconButton")
        self.menu_btn.clicked.connect(self.toggle_left_widget)

        menu_layout = QVBoxLayout()
        menu_layout.addWidget(self.menu_btn)
        menu_layout.addStretch()
        self.menu_widget = QWidget()
        self.menu_widget.setLayout(menu_layout)
        self.menu_widget.setMaximumWidth(60)

        # === Buttons (העבר לצד ימין למעלה) ===
        add_btn = QPushButton()
        add_btn.setIcon(QIcon("frontend/assets/icons/plus.svg"))
        add_btn.setToolTip("Add new plane")
        add_btn.setFixedSize(42, 42)
        add_btn.setObjectName("RoundIconButton")
        add_btn.clicked.connect(self.presenter.open_add_plane)

        refresh_btn = QPushButton()
        refresh_btn.setIcon(QIcon("frontend/assets/icons/refresh.svg"))
        refresh_btn.setToolTip("Refresh plane list")
        refresh_btn.setFixedSize(42, 42)
        refresh_btn.setObjectName("RoundIconButton")
        refresh_btn.clicked.connect(self.presenter.load_planes)

        top_bar = QHBoxLayout()
        top_bar.addWidget(add_btn)
        top_bar.addWidget(refresh_btn)
        top_bar.addStretch()
        top_bar.setContentsMargins(10, 10, 10, 10)
        top_bar_widget = QWidget()
        top_bar_widget.setLayout(top_bar)

        # === RIGHT: Plane Details Card ===
        self.detail_container = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_container)
        self.detail_layout.setAlignment(Qt.AlignTop)

        # === Combine Layouts ===
        self.content_layout = QHBoxLayout()
        self.content_layout.addWidget(
            self.menu_widget, alignment=Qt.AlignLeft | Qt.AlignTop
        )
        self.content_layout.addSpacing(40)
        right_panel = QVBoxLayout()
        right_panel.addWidget(top_bar_widget, alignment=Qt.AlignRight)
        right_panel.addWidget(self.detail_container)
        right_panel.addStretch()
        self.right_panel_widget = QWidget()
        self.right_panel_widget.setLayout(right_panel)
        self.content_layout.addWidget(
            self.right_panel_widget, alignment=Qt.AlignVCenter
        )
        self.content_layout.addStretch(1)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.content_layout)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect itemClicked signal to the slot
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
                and (
                    manufacturer == "All Manufacturers" or plane.MadeBy == manufacturer
                )
                and (
                    seat_filter == "All Sizes"
                    or (seat_filter == "Small (≤100)" and total_seats <= 100)
                    or (seat_filter == "Medium (101–250)" and 101 <= total_seats <= 250)
                    or (seat_filter == "Large (>250)" and total_seats > 250)
                )
            ):
                item_text = f"{plane.Name}"
                item = QListWidgetItem(item_text)
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

        card.setFixedWidth(380)
        card.setStyleSheet(
            """
            QFrame#PlaneCard {
                background-color: #1c1c1c;
                border-radius: 12px;
                border: 1px solid #333;
                padding: 12px;
            }
            QLabel#PlaneCardTitle {
                color: #00C2A8;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 6px;
            }
        """
        )

        # === תמונה של המטוס ===
        if plane.Picture:
            try:
                response = requests.get(plane.Picture, timeout=3)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    image_label = QLabel()
                    image_label.setPixmap(
                        pixmap.scaled(
                            300, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation
                        )
                    )
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

    def toggle_left_widget(self):
        """פותח/סוגר את רשימת המטוסים עם אנימציה חלקה"""
        if (
            hasattr(self, "dock_animation")
            and self.dock_animation.state() == QAbstractAnimation.Running
        ):
            return  # למנוע לחיצה כפולה בזמן אנימציה

        start_width = self.left_dock.width()
        end_width = 0 if self.left_dock.isVisible() else 380

        # אם נסגר – נציג לפני שמתחילים להרחיב
        if not self.left_dock.isVisible():
            self.left_dock.show()

        self.dock_animation = QPropertyAnimation(self.left_dock, b"maximumWidth")
        self.dock_animation.setDuration(300)
        self.dock_animation.setStartValue(start_width)
        self.dock_animation.setEndValue(end_width)
        self.dock_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.dock_animation.start()

        # אם נסגר – נסתיר בסוף האנימציה
        if self.left_dock.isVisible() and end_width == 0:
            self.dock_animation.finished.connect(self.left_dock.hide)

    def mousePressEvent(self, event):
        # אם לוחצים מחוץ ל-left_dock והכפתור, הרשימה תיסגר
        if self.left_dock.isVisible():
            global_pos = self.mapToGlobal(event.pos())
            dock_rect = self.left_dock.geometry()
            dock_global = self.left_dock.mapToGlobal(dock_rect.topLeft())
            dock_rect_global = QRect(dock_global, dock_rect.size())
            menu_rect = self.menu_widget.geometry()
            menu_global = self.menu_widget.mapToGlobal(menu_rect.topLeft())
            menu_rect_global = QRect(menu_global, menu_rect.size())
            if not dock_rect_global.contains(
                global_pos
            ) and not menu_rect_global.contains(global_pos):
                self.left_dock.hide()
        super().mousePressEvent(event)
