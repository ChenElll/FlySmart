from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
import requests


class PlaneDetailsDialog(QDialog):
    """
    Dialog window that displays detailed information about a specific plane.
    It is view-only but includes an Edit button that allows users to modify plane data.
    """

    def __init__(self, parent, plane, cache_manager, presenter):
        super().__init__(parent)
        self.plane = plane
        self.cache = cache_manager
        self.presenter = presenter
        self.fields = {}  # will store QLabel references for dynamic updates

        # --- Window setup ---
        self.setWindowTitle(f"Plane Details – {plane.Name}")
        self.setWindowIcon(QIcon("frontend/assets/icons/airplane.svg"))
        self.setMinimumWidth(560)

        # --- Styling ---
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
        """Builds the dialog layout and fills in the plane information."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # --- Header title ---
        title = QLabel(f"✈ {self.plane.Name}")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # --- Details container ---
        frame = QFrame()
        frame.setObjectName("container")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(25, 25, 25, 25)
        frame_layout.setSpacing(14)

        # --- Plane image ---
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

        # --- Plane details ---
        info_texts = [
            ("ID:", str(self.plane.PlaneId)),
            ("Manufacturer:", self.plane.MadeBy),
            ("Year:", str(self.plane.Year)),
            (
                "Seats by Class:",
                f"First: {self.plane.NumOfSeats1} | Business: {self.plane.NumOfSeats2} | Economy: {self.plane.NumOfSeats3}"
            ),
            (
                "Total Seats:",
                str(self.plane.NumOfSeats1 + self.plane.NumOfSeats2 + self.plane.NumOfSeats3)
            ),
            ("Image URL:", self.plane.Picture or "None"),
        ]

        # Build rows dynamically and store label references
        for label_text, value_text in info_texts:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: 600; min-width: 160px; color: #1A2C3A;")
            val = QLabel(value_text)
            val.setStyleSheet("color: #3C4E56;")
            row.addWidget(lbl)
            row.addWidget(val)
            frame_layout.addLayout(row)
            self.fields[label_text] = val  # store reference for later update

        layout.addWidget(frame)

        # --- Edit button ---
        edit_btn = QPushButton("Edit Plane")
        edit_btn.setObjectName("edit")
        edit_btn.setFixedWidth(180)
        edit_btn.clicked.connect(self._edit_plane)
        layout.addWidget(edit_btn, alignment=Qt.AlignCenter)

    # ------------------------------------------------------------
    def _load_image(self):
        """Loads the plane image from a URL or uses a fallback icon if unavailable."""
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
        """Opens the Edit Plane dialog and refreshes data after editing."""
        try:
            self.presenter.open_edit_plane(self.plane)
            # Refresh updated data from the backend
            refreshed = self.presenter.get_plane_by_id(self.plane.PlaneId)
            if refreshed:
                self.plane = refreshed
                self._rebuild_after_update()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open edit dialog:\n{e}")

    # ------------------------------------------------------------
    def _rebuild_after_update(self):
        """Refreshes all displayed information after the plane is edited."""
        # Update title
        self.layout().itemAt(0).widget().setText(f"✈ {self.plane.Name}")

        # Update textual fields
        self.fields["Manufacturer:"].setText(self.plane.MadeBy)
        self.fields["Year:"].setText(str(self.plane.Year))
        self.fields["Seats by Class:"].setText(
            f"First: {self.plane.NumOfSeats1} | Business: {self.plane.NumOfSeats2} | Economy: {self.plane.NumOfSeats3}"
        )
        self.fields["Total Seats:"].setText(
            str(self.plane.NumOfSeats1 + self.plane.NumOfSeats2 + self.plane.NumOfSeats3)
        )
        self.fields["Image URL:"].setText(self.plane.Picture or "None")

        # Reload image (in case it changed)
        self._load_image()
