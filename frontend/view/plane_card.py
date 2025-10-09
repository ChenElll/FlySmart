from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, Signal
from PySide6.QtGui import QColor, QPixmap
from .image_loader import ImageLoader


class PlaneCard(QFrame):
    """Display card representing a single plane, including image, details, and hover effects."""
    clicked = Signal(object)  # Emits the plane object when clicked

    def __init__(self, plane, cache_manager, presenter):
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
        """Builds the visual layout of the plane card."""
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

        # Subtle shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

        # Plane image placeholder
        self.img = QLabel()
        self.img.setFixedSize(QSize(260, 150))
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setScaledContents(False)
        layout.addWidget(self.img, alignment=Qt.AlignCenter)

        # Plane name
        name = QLabel(self.plane.Name)
        name.setObjectName("cardTitle")
        name.setAlignment(Qt.AlignCenter)
        layout.addWidget(name)

        # Plane info line
        total = self.plane.NumOfSeats1 + self.plane.NumOfSeats2 + self.plane.NumOfSeats3
        info = QLabel(f"{self.plane.MadeBy} · {self.plane.Year} · Seats: {total}")
        info.setObjectName("cardSub")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

    # ------------------------------------------------------------
    def _load_image(self):
        """Loads the plane image from cache or downloads it if needed."""
        if not self.plane.Picture:
            self._fade_in_image(QPixmap("frontend/assets/icons/airplane.svg"))
            return

        if self.plane.Picture in self.cache.cache:
            pix = self.cache.cache[self.plane.Picture]
            if pix and not pix.isNull():
                self._fade_in_image(pix)
                return

        loader = ImageLoader(self.plane.Picture)
        loader.finished.connect(lambda url, pix: self._update_image(url, pix))
        loader.load()

    def _update_image(self, url, pix):
        """Called when the image is loaded asynchronously."""
        if self._destroyed:
            return

        if not pix or pix.isNull():
            self._fade_in_image(QPixmap("frontend/assets/icons/airplane.svg"))
            return

        self.cache.cache[url] = pix
        self._fade_in_image(pix)

    # ------------------------------------------------------------
    def _fade_in_image(self, pix):
        """Applies a fade-in animation when the image appears."""
        if self._destroyed:
            return

        if pix is None or not hasattr(pix, "scaled") or pix.isNull():
            pix = QPixmap("frontend/assets/icons/airplane.svg")

        scaled = pix.scaled(
            self.img.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.img.setPixmap(scaled)

        opacity = QGraphicsOpacityEffect()
        self.img.setGraphicsEffect(opacity)
        anim = QPropertyAnimation(opacity, b"opacity")
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()
        self.img._fade_anim = anim

    # ------------------------------------------------------------
    def enterEvent(self, event):
        """Hover effect: soft shadow, light background, and slight upward lift."""
        eff = self.graphicsEffect()
        if isinstance(eff, QGraphicsDropShadowEffect):
            eff.setBlurRadius(60)
            eff.setOffset(0, 12)
            eff.setColor(QColor(0, 0, 0, 90))

        # Subtle background color change
        self.setStyleSheet(self.styleSheet() + """
            QFrame {
                background-color: #F9FCFF;
                border: 1px solid #B5D9E8;
            }
        """)

        # Lift animation
        self._hover_anim = QPropertyAnimation(self, b"geometry")
        self._hover_anim.setDuration(150)
        start_rect = self.geometry()
        end_rect = start_rect.translated(0, -6)
        self._hover_anim.setStartValue(start_rect)
        self._hover_anim.setEndValue(end_rect)
        self._hover_anim.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Restores card position, shadow, and colors when hover ends."""
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

        # Return animation
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
        """Emit signal when card is clicked."""
        if not self._destroyed:
            self.clicked.emit(self.plane)
