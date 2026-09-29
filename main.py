import sys
from PyQt6.QtWidgets import (
    QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout)
from PyQt6.QtCore import Qt
from top_cornerButton import PageButton, Pages
from sidebar import Sidebar, SidebarButton


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Getting started | MYnotion")
        self.resize(700, 500)

        # white background, dark text so it also looks right on a dark system theme
        self.setStyleSheet("""
            * { color: #222222; }
            QMainWindow, #central { background-color: white; }
            QMainWindow::separator { background-color: #dddddd; width: 1px; height: 1px; }
        """)

        central_widget = QWidget()
        central_widget.setObjectName("central")
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # all the pages live here, everything else just reads from it
        self.pages = Pages("Getting started")
        # self.pages.add("Ideas", "💡")   # uncomment to test more pages in the popup / sidebar

        # sidebar starts hidden, on the left
        self.sidebar = Sidebar(self.pages)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidebar)
        self.sidebar.hide()

        # top row: 3 line button, then the page button
        top_bar = QHBoxLayout()
        top_bar.setSpacing(4)

        top_bar.addWidget(SidebarButton(self.pages, self.sidebar))

        self.getting_started = PageButton(self.pages)
        top_bar.addWidget(self.getting_started)

        top_bar.addStretch()

        layout.addLayout(top_bar)

        self.pages.changed.connect(self.page_name_changed)#changing to the live typing thing i did

        layout.addStretch()

    #adding the changing thing
    def page_name_changed(self):
        self.setWindowTitle(f"{self.pages.name} | MYnotion")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())