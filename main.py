import sys
from PyQt6.QtWidgets import (
    QApplication,QMainWindow,QWidget,QVBoxLayout)
from top_cornerButton import PageButton


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Getting started | MYnotion")
        self.resize(700, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        self.getting_started = PageButton("Getting started")
        layout.addWidget(self.getting_started)

        self.getting_started.name_changed.connect(self.page_name_changed)#changing to the live typing thing i did

        layout.addStretch()

    #adding the changing thing
    def page_name_changed(self, name):
        self.setWindowTitle(f"{name} | MYnotion")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())