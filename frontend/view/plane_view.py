from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QMessageBox
)

class PlaneView(QMainWindow):
    def __init__(self, presenter):
        super().__init__()
        self.presenter = presenter
        self.setWindowTitle("✈ FlySmart - Plane Management")
        self.resize(800, 400)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Year", "Made By", "Picture", "Seats1", "Seats2", "Seats3"
        ])

        layout = QVBoxLayout()
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_planes(self, planes):
        self.table.setRowCount(len(planes))
        for row, plane in enumerate(planes):
            self.table.setItem(row, 0, QTableWidgetItem(str(plane.PlaneId)))
            self.table.setItem(row, 1, QTableWidgetItem(plane.Name))
            self.table.setItem(row, 2, QTableWidgetItem(str(plane.Year)))
            self.table.setItem(row, 3, QTableWidgetItem(plane.MadeBy))
            self.table.setItem(row, 4, QTableWidgetItem(plane.Picture or ""))
            self.table.setItem(row, 5, QTableWidgetItem(str(plane.NumOfSeats1)))
            self.table.setItem(row, 6, QTableWidgetItem(str(plane.NumOfSeats2)))
            self.table.setItem(row, 7, QTableWidgetItem(str(plane.NumOfSeats3)))

    def show_error(self, message: str):
        QMessageBox.critical(self, "Error", message)
