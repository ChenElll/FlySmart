import sys
import traceback
from PySide6.QtWidgets import QApplication, QMessageBox
from frontend.view.plane_view import PlaneView
from frontend.presenter.plane_presenter import PlanePresenter

# זמנית, בתחילת main.py
from frontend.model.plane_entity import PlaneEntity
import inspect
print("PlaneEntity loaded from:", inspect.getfile(PlaneEntity))
print("create type:", type(PlaneEntity.create))


# --- טיפול כולל בשגיאות כדי למנוע סגירה פתאומית ---
def _exception_hook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        print("⛔ Unexpected Error:\n", tb)
        msg = QMessageBox()
        msg.setWindowTitle("Unexpected Error")
        msg.setIcon(QMessageBox.Critical)
        msg.setText("An unexpected error occurred.")
        msg.setDetailedText(tb)
        msg.exec()
    except Exception:
        # fallback למקרה שאין QApplication פעיל
        print(tb, file=sys.stderr)
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = _exception_hook

# --- הפונקציה הראשית ---
def main():
    app = QApplication(sys.argv)

    presenter = PlanePresenter(None)
    view = PlaneView(presenter)
    presenter.view = view

    # הצגת חלון
    view.show()

    try:
        sys.exit(app.exec())
    except Exception:
        # במקרה שמשהו קורס תוך כדי לולאת האירועים
        tb = traceback.format_exc()
        print("Crash inside app.exec():\n", tb)
        msg = QMessageBox()
        msg.setWindowTitle("Critical Crash")
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Application crashed.")
        msg.setDetailedText(tb)
        msg.exec()
        sys.exit(1)

if __name__ == "__main__":
    main()
