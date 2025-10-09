import sys
import traceback
from PySide6.QtWidgets import QApplication, QMessageBox
from frontend.view.plane_view import PlaneView
from frontend.presenter.plane_presenter import PlanePresenter



# --- Global Exception Handler ---
# This function catches any unhandled exceptions to prevent the app from closing abruptly.
# It displays the error both in the console and as a GUI dialog for debugging convenience.
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
        # Fallback if no QApplication is active
        print(tb, file=sys.stderr)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


# Replace Python’s default exception handler with our custom one
sys.excepthook = _exception_hook


# --- Main Entry Point ---
# Initializes the application, connects the Presenter and View,
# and starts the main event loop.
def main():
    app = QApplication(sys.argv)

    # Create Presenter and View instances
    presenter = PlanePresenter(None)
    view = PlaneView(presenter)
    presenter.view = view  # Establish two-way connection (MVP pattern)

    # Show the main window
    view.show()

    # Center the window on the user's screen
    frame_geom = view.frameGeometry()
    screen_center = app.primaryScreen().availableGeometry().center()
    frame_geom.moveCenter(screen_center)
    view.move(frame_geom.topLeft())

    # Start the main event loop safely
    try:
        sys.exit(app.exec())
    except Exception:
        # Capture unexpected crashes during app runtime
        tb = traceback.format_exc()
        print("Crash inside app.exec():\n", tb)
        msg = QMessageBox()
        msg.setWindowTitle("Critical Crash")
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Application crashed.")
        msg.setDetailedText(tb)
        msg.exec()
        sys.exit(1)


# Entry point when the script is run directly
if __name__ == "__main__":
    main()
