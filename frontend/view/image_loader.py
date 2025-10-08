from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap
import requests


class ImageLoader(QObject):
    """טעינת תמונות פשוטה – ללא threads"""
    finished = Signal(str, QPixmap)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def load(self):
        """מוריד תמונה (סינכרוני) ושולח Pixmap מוכן"""
        if not self.url:
            self.finished.emit(self.url, QPixmap())
            return

        pix = QPixmap()
        try:
            if self.url.startswith("http"):
                r = requests.get(self.url, timeout=3)
                if r.status_code == 200:
                    pix.loadFromData(r.content)
            else:
                pix.load(self.url)
        except Exception:
            pass

        self.finished.emit(self.url, pix)
