from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, Signal
from PySide6.QtGui import QColor, QPixmap
from .image_loader import ImageLoader


class PlaneCard(QFrame):
    """UI card displaying a single plane, including image, info, and hover animations."""
    clicked = Signal(object)  # Emits the Plane object when the card is clicked

    def __init__(self, plane, cache_manager, presenter):
        """Initialize the card with plane data, cache manager, and presenter."""
        super().__init__()
        self.plane = plane
        self.cache = cache_manager
        self.presenter = presenter
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(340, 290)
        self._destroyed = False

        self._build_ui()
        self._load_image()

    # ------------------------------------------------------------
    def _build_ui(self):
        """Creates the visual structure of the plane card."""
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 18px;
                border: 1px solid #D8E8EE;
            }
            QLabel#cardTitle {
                font-size: 16px;
                font-weight: 600;
                color: #1A2C3A;
            }
            QLabel#cardSub {
                font-size: 13px;
                color: #5A6D78;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Subtle shadow around each card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

        # Image placeholder (before the real image loads)
        self.img = QLabel()
        self.img.setFixedSize(QSize(260, 150))
        self.img.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.img, alignment=Qt.AlignCenter)

        # Plane name
        name = QLabel(self.plane.Name)
        name.setObjectName("cardTitle")
        name.setAlignment(Qt.AlignCenter)
        layout.addWidget(name)

        # Plane info line (manufacturer, year, seat count)
        total = self.plane.NumOfSeats1 + self.plane.NumOfSeats2 + self.plane.NumOfSeats3
        info = QLabel(f"{self.plane.MadeBy} · {self.plane.Year} · Seats: {total}")
        info.setObjectName("cardSub")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

    # ------------------------------------------------------------
    def _load_image(self):
        """Loads the plane image asynchronously using ImageLoader.
        This ensures the UI remains responsive while images are downloading."""
        if not self.plane.Picture:
            self._fade_in_image(QPixmap("frontend/assets/icons/airplane.svg"))
            return

        loader = ImageLoader(self.plane.Picture)
        loader.finished.connect(lambda url, pix: self._update_image_and_cleanup(loader, url, pix))
        loader.load()

    def _update_image_and_cleanup(self, loader, url, pix):
        """Triggered once the background thread finishes loading the image."""
        self._update_image(url, pix)

    def _update_image(self, url, pix):
        """Updates the card with the newly loaded image."""
        if self._destroyed:
            return

        # Use fallback icon if image failed to load
        if not pix or pix.isNull():
            self._fade_in_image(QPixmap("frontend/assets/icons/airplane.svg"))
            return

        # Cache the image for later reuse
        self.cache.cache[url] = pix
        self._fade_in_image(pix)

    # ------------------------------------------------------------
    def _fade_in_image(self, pix):
        """Applies a fade-in animation when displaying the image."""
        if self._destroyed:
            return

        if pix is None or not hasattr(pix, "scaled") or pix.isNull():
            pix = QPixmap("frontend/assets/icons/airplane.svg")

        # Scale and show image
        scaled = pix.scaled(self.img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img.setPixmap(scaled)

        # Fade-in effect for smooth visual appearance
        opacity = QGraphicsOpacityEffect()
        self.img.setGraphicsEffect(opacity)
        anim = QPropertyAnimation(opacity, b"opacity")
        anim.setDuration(600)
        anim.setStartValue(0.3)
        anim.setEndValue(1)
        anim.start()
        self.img._fade_anim = anim  # Keep reference to prevent garbage collection

    # ------------------------------------------------------------
    def enterEvent(self, event):
        """Hover effect: raises the card slightly and adds stronger shadow."""
        eff = self.graphicsEffect()
        if isinstance(eff, QGraphicsDropShadowEffect):
            eff.setBlurRadius(60)
            eff.setOffset(0, 12)
            eff.setColor(QColor(0, 0, 0, 90))

        # Change background color subtly
        self.setStyleSheet(self.styleSheet() + """
            QFrame {
                background-color: #F9FCFF;
                border: 1px solid #B5D9E8;
            }
        """)

        # Small upward "lift" animation
        self._hover_anim = QPropertyAnimation(self, b"geometry")
        self._hover_anim.setDuration(150)
        start_rect = self.geometry()
        end_rect = start_rect.translated(0, -6)
        self._hover_anim.setStartValue(start_rect)
        self._hover_anim.setEndValue(end_rect)
        self._hover_anim.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Reverses hover effects when the mouse leaves the card."""
        eff = self.graphicsEffect()
        if isinstance(eff, QGraphicsDropShadowEffect):
            eff.setBlurRadius(30)
            eff.setOffset(0, 5)
            eff.setColor(QColor(0, 0, 0, 25))

        self.setStyleSheet(self.styleSheet() + """
            QFrame {
                background-color: white;
                border: 1px solid #D8E8EE;
            }
        """)

        # Drop animation (return to original position)
        self._hover_back_anim = QPropertyAnimation(self, b"geometry")
        self._hover_back_anim.setDuration(150)
        end_rect = self.geometry()
        start_rect = end_rect.translated(0, 6)
        self._hover_back_anim.setStartValue(end_rect)
        self._hover_back_anim.setEndValue(start_rect)
        self._hover_back_anim.start()

        super().leaveEvent(event)

    # ------------------------------------------------------------
    def mousePressEvent(self, event):
        """Emits a signal when the card is clicked, passing the plane object."""
        if not self._destroyed:
            self.clicked.emit(self.plane)
