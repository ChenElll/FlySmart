import sys
from PySide6.QtWidgets import QApplication
from frontend.view.plane_view import PlaneView
from frontend.presenter.plane_presenter import PlanePresenter

def main():
    app = QApplication(sys.argv)
    view = PlaneView(None)
    presenter = PlanePresenter(view)
    view.presenter = presenter

    presenter.load_planes()
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
