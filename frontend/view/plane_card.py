from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, Signal
from PySide6.QtGui import QColor, QPixmap
from .image_loader import ImageLoader


class PlaneCard(QFrame):
    clicked = Signal(object)  # שידור לחיצה עם אובייקט המטוס

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
        # עיצוב בסיסי
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

        # צל קל
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

        # תמונה
        self.img = QLabel()
        self.img.setFixedSize(QSize(260, 150))
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setPixmap(QPixmap("frontend/assets/icons/airplane.svg"))
        layout.addWidget(self.img, alignment=Qt.AlignCenter)

        # שם המטוס
        name = QLabel(self.plane.Name)
        name.setObjectName("cardTitle")
        name.setAlignment(Qt.AlignCenter)
        layout.addWidget(name)

        # פרטים נוספים
        total = self.plane.NumOfSeats1 + self.plane.NumOfSeats2 + self.plane.NumOfSeats3
        info = QLabel(f"{self.plane.MadeBy} · {self.plane.Year} · Seats: {total}")
        info.setObjectName("cardSub")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

    # ------------------------------------------------------------
    def _load_image(self):
        """טעינת תמונה פשוטה (ללא thread)"""
        if not self.plane.Picture:
            return

        # אם התמונה קיימת כבר ב־cache → נשתמש בה מיד
        if self.plane.Picture in self.cache.cache:
            pix = self.cache.cache[self.plane.Picture]
            if not pix.isNull():
                self._fade_in_image(pix)
            return

        # אחרת נטען אותה
        loader = ImageLoader(self.plane.Picture)
        loader.finished.connect(lambda url, pix: self._update_image(url, pix))
        loader.load()

    def _update_image(self, url, pix):
        """מציג את התמונה אם קיימת"""
        if not pix or pix.isNull() or self._destroyed:
            return

        self.cache.cache[url] = pix
        self._fade_in_image(pix)

    def _fade_in_image(self, pix):
        """אפקט טעינה רך"""
        if self._destroyed:
            return

        self.img.setPixmap(
            pix.scaled(self.img.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        )
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
        """אפקט hover עדין"""
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(180)
        anim.setStartValue(self.geometry())
        g = self.geometry()
        anim.setEndValue(g.adjusted(-3, -3, 3, 3))
        anim.start()
        self._hover_anim = anim
        super().enterEvent(event)

    def leaveEvent(self, event):
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(180)
        g = self.geometry()
        anim.setStartValue(g)
        anim.setEndValue(g.adjusted(3, 3, -3, -3))
        anim.start()
        self._hover_anim = anim
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if not self._destroyed:
            self.clicked.emit(self.plane)
