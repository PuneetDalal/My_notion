from PyQt6.QtWidgets import (
    QDockWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from PyQt6.QtCore import Qt
from top_cornerButton import PageList, PagesPopup, HoverPopup


class Sidebar(QDockWidget):
    # the pinned sidebar: drag its top strip to move it,
    # it snaps to the left or right edge of the window (top / bottom ignored)

    def __init__(self, pages):
        super().__init__()

        # only left / right edges, and it can't float away or be closed
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.setMinimumWidth(200)

        # top strip = the handle you drag
        grip = QLabel("Pages")
        grip.setToolTip("Drag to move the sidebar left / right")
        grip.setCursor(Qt.CursorShape.SizeAllCursor)

        grip.setStyleSheet("""
            QLabel {
                background-color: white;
                color: #888888;
                font-size: 12px;
                padding: 8px 12px;
            }
        """)

        self.setTitleBarWidget(grip)

        # same page list as the hover popup, always vertical
        body = QWidget()
        body.setObjectName("body")
        body.setStyleSheet("QWidget#body { background-color: white; }")

        layout = QVBoxLayout(body)
        layout.setContentsMargins(6, 0, 6, 6)

        layout.addWidget(PageList(pages))

        layout.addStretch()

        self.setWidget(body)


class SidebarButton(QPushButton):
    # 3 line button: hover shows the pages popup, click pins / unpins the sidebar

    def __init__(self, pages, sidebar):
        super().__init__("☰")
        self.sidebar = sidebar

        self.setFixedSize(32, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                font-size: 18px;
            }

            QPushButton:hover {
                background-color: #eeeeee;
                border: 1px solid #cccccc;
            }

            QPushButton:pressed {
                background-color: #e2e2e2;
            }
        """)

        self.popup = PagesPopup(self, pages)

        # no hover popup while the sidebar is pinned
        self.hover = HoverPopup(self, self.popup, lambda: not sidebar.isVisible())

        self.clicked.connect(self.toggle)

    def toggle(self):

        self.popup.hide()

        self.sidebar.setVisible(not self.sidebar.isVisible())