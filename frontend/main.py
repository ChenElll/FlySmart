import sys
from PySide6.QtWidgets import QApplication
from frontend.view.plane_view import PlaneView
from frontend.presenter.plane_presenter import PlanePresenter

def main():
    app = QApplication(sys.argv)

    # יצירת presenter ריק בינתיים (בלי view)
    presenter = PlanePresenter(None)

    # יצירת view תוך הזרקת presenter
    view = PlaneView(presenter)

    # חיבור הדדי
    presenter.view = view

    # טוענים את רשימת המטוסים
    presenter.load_planes()

    # הצגת חלון
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
