from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QPixmap
import requests


class ImageLoader(QObject):
    """Asynchronous image loader using QThread.

    This class downloads an image (either from the web or a local path)
    in a separate background thread, to prevent blocking the UI.
    Once the image is ready, it emits the 'finished' signal with the URL
    and the resulting QPixmap object.
    """

    # Signal emitted when the image is fully loaded (url, pixmap)
    finished = Signal(str, QPixmap)

    def __init__(self, url: str):
        """Initialize the loader with the image URL or file path."""
        super().__init__()
        self.url = url
        self._thread = None  # Each loader instance manages its own QThread

    def load(self):
        """Starts the image loading process asynchronously."""
        if not self.url:
            # Emit an empty pixmap immediately if URL is missing
            self.finished.emit(self.url, QPixmap())
            return

        # Create a background thread dedicated to this loader
        self._thread = QThread()
        self.moveToThread(self._thread)

        # Connect thread start → actual loading function
        self._thread.started.connect(self._do_load)

        # Ensure proper cleanup when thread finishes
        self._thread.finished.connect(self._thread.deleteLater)

        # Start the background thread
        self._thread.start()

    def _do_load(self):
        """Executed inside the background thread.
        Performs the actual image download (non-blocking for the UI)."""
        pix = QPixmap()
        try:
            if self.url.startswith("http"):
                # Load image from a remote URL
                r = requests.get(self.url, timeout=4)
                if r.status_code == 200:
                    pix.loadFromData(r.content)
            else:
                # Load image from local filesystem
                pix.load(self.url)
        except Exception:
            # Silent fail: emit empty pixmap if download fails
            pass

        # Notify listeners (e.g., PlaneCard) that image is ready
        self.finished.emit(self.url, pix)

        # Gracefully stop the worker thread (no blocking)
        self._thread.quit()
