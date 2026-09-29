import sys
from PyQt6.QtWidgets import (
    QApplication,QMainWindow,QWidget,QVBoxLayout)
from top_cornerButton import PageButton


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MYnotion")
        self.resize(700, 500)
        central_widget = QWidget()

        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        self.getting_started = PageButton("Getting started")
        layout.addWidget( self.getting_started)
        layout.addStretch()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())