from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QMessageBox,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
    QComboBox,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QLinearGradient, QPalette, QColor, QBrush, QIcon

from .plane_card import PlaneCard
from .plane_details_dialog import PlaneDetailsDialog
from .plane_stats_dialog import PlaneStatsDialog


# ============================================================
# Simple cache for storing loaded images (QPixmaps)
# ============================================================
class SimpleCache:
    def __init__(self):
        self.cache = {}  # URL or path → QPixmap


# ============================================================
# Custom ComboBox allowing multiple selections with checkboxes
# ============================================================
class MultiSelectComboBox(QComboBox):
    selection_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.popup_widget = QListWidget()
        self.setModel(self.popup_widget.model())
        self.setView(self.popup_widget)
        self.popup_widget.itemChanged.connect(self.update_selection)

    def set_items(self, items):
        """Fill the combo box with a list of checkable items."""
        self.popup_widget.clear()
        for item_text in items:
            item = QListWidgetItem(item_text)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.popup_widget.addItem(item)

    def update_selection(self):
        """Update the displayed text and emit the selected items list."""
        selected = [
            self.popup_widget.item(i).text()
            for i in range(self.popup_widget.count())
            if self.popup_widget.item(i).checkState() == Qt.Checked
        ]
        self.lineEdit().setText(", ".join(selected) if selected else "")
        self.selection_changed.emit(selected)


# ============================================================
# Plane Management View – main window of the application
# Displays plane cards, filters, and statistics
# ============================================================
class PlaneView(QWidget):
    def __init__(self, presenter):
        super().__init__()
        self.presenter = presenter
        self.presenter.view = self

        # Initialize cache for images
        self.cache_manager = SimpleCache()

        # --- Window properties ---
        self.setWindowTitle("FlySmart | Plane Manager")
        self.setWindowIcon(QIcon("frontend/assets/icons/airplane.svg"))
        self.resize(1200, 780)

        # Light blue gradient background
        palette = QPalette()
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor("#FFFFFF"))
        grad.setColorAt(1, QColor("#EAF5FA"))
        palette.setBrush(QPalette.Window, QBrush(grad))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # Global style for the window
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

        # Build the user interface
        self.init_ui()

        # Load initial planes through the presenter
        self.presenter.load_planes()

    # ============================================================
    # UI Construction
    # ============================================================
    def init_ui(self):
        """Build the main screen layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # --- Header (title and buttons) ---
        header = QHBoxLayout()
        title = QLabel("Plane Manager")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()

        # Button: show statistics window
        self.stats_button = QPushButton("Show Statistics")
        self.stats_button.setObjectName("addBtn")
        self.stats_button.clicked.connect(self.show_stats_dialog)
        header.addWidget(self.stats_button)
        header.addSpacing(8)

        # Button: add new plane
        add_btn = QPushButton("+ Add Plane")
        add_btn.setObjectName("addBtn")
        add_btn.clicked.connect(self.presenter.open_add_plane)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # --- Filters section ---
        filters = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or manufacturer...")
        self.search_input.textChanged.connect(self.apply_filters)

        self.made_by_combo = MultiSelectComboBox()
        self.made_by_combo.lineEdit().setPlaceholderText("Select manufacturers...")
        self.made_by_combo.selection_changed.connect(self.apply_filters)

        self.year_combo = MultiSelectComboBox()
        self.year_combo.lineEdit().setPlaceholderText("Select years...")
        self.year_combo.selection_changed.connect(self.apply_filters)

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("clearBtn")
        clear_btn.clicked.connect(self.reset_filters)

        filters.addWidget(self.search_input, 3)
        filters.addWidget(self.made_by_combo)
        filters.addWidget(self.year_combo)
        filters.addWidget(clear_btn)
        layout.addLayout(filters)

        # --- Scroll area with plane cards ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        container = QWidget()
        self.cards_layout = QGridLayout(container)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        self.cards_layout.setSpacing(18)
        self.cards_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.scroll.setWidget(container)
        layout.addWidget(self.scroll)

        # --- Status bar ---
        self.status_label = QLabel("Status: ⏳ Loading...")
        self.status_label.setObjectName("status")
        layout.addWidget(self.status_label)

    # ------------------------------------------------------------
    def show_status(self, text):
        """Update status label with new message."""
        self.status_label.setText(f"Status: {text}")

    # ============================================================
    # Display planes list
    # ============================================================
    def show_planes(self, planes):
        """Display all loaded planes and refresh filters."""
        self.planes = planes
        makers = sorted(set(p.MadeBy for p in planes if p.MadeBy))
        years = sorted(set(str(p.Year) for p in planes if p.Year))

        self.made_by_combo.set_items(makers)
        self.year_combo.set_items(years)

        # Reset previous selections
        for combo in [self.made_by_combo, self.year_combo]:
            combo.lineEdit().clear()
            for i in range(combo.popup_widget.count()):
                item = combo.popup_widget.item(i)
                item.setCheckState(Qt.Unchecked)

        self.apply_filters()
        self.show_status(f"✅ Loaded {len(planes)} planes")

        # Refresh stats dialog if it's open
        if (
            hasattr(self, "stats_dialog")
            and self.stats_dialog
            and self.stats_dialog.isVisible()
        ):
            self.stats_dialog.update_charts(planes)

    # ============================================================
    # Filtering logic
    # ============================================================
    def apply_filters(self):
        """Filter plane list based on search text, manufacturer, and year."""
        if not hasattr(self, "planes"):
            return

        search_text = self.search_input.text().strip().lower()
        selected_makers = (
            self.made_by_combo.lineEdit().text().split(", ")
            if self.made_by_combo.lineEdit().text()
            else []
        )
        selected_years = (
            self.year_combo.lineEdit().text().split(", ")
            if self.year_combo.lineEdit().text()
            else []
        )

        filtered = []
        for p in self.planes:
            match_name = (
                search_text in p.Name.lower() or search_text in p.MadeBy.lower()
            )
            match_maker = not selected_makers or p.MadeBy in selected_makers
            match_year = not selected_years or str(p.Year) in selected_years
            if match_name and match_maker and match_year:
                filtered.append(p)

        self.display_cards(filtered)

        # Update statistics if window is open
        if (
            hasattr(self, "stats_dialog")
            and self.stats_dialog
            and self.stats_dialog.isVisible()
        ):
            self.stats_dialog.update_charts(filtered)

    def reset_filters(self):
        """Clear all filter selections and show all planes again."""
        self.search_input.clear()
        for combo in [self.made_by_combo, self.year_combo]:
            combo.lineEdit().clear()
            for i in range(combo.popup_widget.count()):
                item = combo.popup_widget.item(i)
                item.setCheckState(Qt.Unchecked)
        self.apply_filters()

    # ============================================================
    # Plane cards display
    # ============================================================
    def display_cards(self, planes):
        """Render plane cards inside the scrollable grid."""
        for i in reversed(range(self.cards_layout.count())):
            w = self.cards_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        self._pending_planes = list(planes)
        self._current_index = 0

        def load_next_batch():
            """Load plane cards gradually for smooth UI performance."""
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
    # Plane details dialog
    # ============================================================
    def open_plane_details(self, plane):
        """Open modal dialog showing plane details."""
        dialog = PlaneDetailsDialog(self, plane, self.cache_manager, self.presenter)
        self.active_details_dialog = dialog
        dialog.exec()
        self.active_details_dialog = None

    # ============================================================
    # Plane card helper functions
    # ============================================================
    def add_plane_card(self, plane):
        """Add new plane card to grid layout."""
        card = PlaneCard(plane, self.cache_manager, self.presenter)
        card.clicked.connect(lambda p=plane: self.open_plane_details(p))
        total = self.cards_layout.count()
        row, col = divmod(total, 3)
        self.cards_layout.addWidget(card, row, col)
        self.show_status(f"✅ Plane '{plane.Name}' added.")

    def refresh_plane_card(self, updated_plane):
        """Refresh a plane card after editing its details."""
        for i in range(self.cards_layout.count()):
            w = self.cards_layout.itemAt(i).widget()
            if hasattr(w, "plane") and w.plane.PlaneId == updated_plane.PlaneId:
                w.plane = updated_plane
                w._fade_in_image(None)
                w.repaint()
                break
        self.show_status(f"✏️ Plane '{updated_plane.Name}' updated.")

    def remove_plane_card(self, plane_id):
        """Remove plane card and close its details dialog if open."""
        if hasattr(self, "active_details_dialog") and self.active_details_dialog:
            try:
                if (
                    hasattr(self.active_details_dialog, "plane")
                    and self.active_details_dialog.plane.PlaneId == plane_id
                ):
                    self.active_details_dialog.close()
                    self.active_details_dialog = None
            except Exception:
                pass

        for i in reversed(range(self.cards_layout.count())):
            w = self.cards_layout.itemAt(i).widget()
            if hasattr(w, "plane") and w.plane.PlaneId == plane_id:
                w.deleteLater()
                break

        self.show_status("🗑️ Plane deleted successfully.")

    # ============================================================
    # Statistics window
    # ============================================================
    def show_stats_dialog(self):
        """Open or refresh the statistics dialog window."""
        filtered_planes = []
        if hasattr(self, "_pending_planes"):
            filtered_planes = self._pending_planes
        elif hasattr(self, "planes"):
            filtered_planes = self.planes

        if not filtered_planes:
            QMessageBox.information(self, "No Data", "No planes to display in statistics.")
            return

        if (
            hasattr(self, "stats_dialog")
            and self.stats_dialog
            and self.stats_dialog.isVisible()
        ):
            self.stats_dialog.update_charts(filtered_planes)
            self.stats_dialog.raise_()
            self.stats_dialog.activateWindow()
        else:
            self.stats_dialog = PlaneStatsDialog(filtered_planes, self)
            self.stats_dialog.show()

    # ============================================================
    # Error message helper
    # ============================================================
    def show_error(self, msg):
        """Display a critical error message dialog."""
        QMessageBox.critical(self, "Error", msg)
