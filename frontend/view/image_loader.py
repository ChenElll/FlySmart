from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QPixmap
import requests

class ImageLoader(QObject):
    finished = Signal(str, QPixmap)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self._thread = None

    def load(self):
        if not self.url:
            self.finished.emit(self.url, QPixmap())
            return

        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self._do_load)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _do_load(self):
        pix = QPixmap()
        try:
            if self.url.startswith("http"):
                r = requests.get(self.url, timeout=4)
                if r.status_code == 200:
                    pix.loadFromData(r.content)
            else:
                pix.load(self.url)
        except Exception:
            pass
        self.finished.emit(self.url, pix)
        self._thread.quit()
