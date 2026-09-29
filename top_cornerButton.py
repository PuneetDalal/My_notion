from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QFrame,
    QSizePolicy,
    QLineEdit
)
from PyQt6.QtCore import (
    Qt,
    QTimer,
    QEvent,
    QObject,
    pyqtSignal
)

# same look for every popup window (page list, rename)
POPUP_STYLE = """
    QFrame {
        background-color: white;
        border: 1px solid #dddddd;
        border-radius: 8px;
    }
"""

# one page in the list: grey under the mouse, light sky blue for the page we are on
ROW_STYLE = """
    QPushButton {
        background-color: transparent;
        border: none;
        border-radius: 5px;
        padding: 7px 12px;
        text-align: left;
        font-size: 13px;
    }

    QPushButton:hover {
        background-color: #eeeeee;
    }

    QPushButton[current="true"] {
        background-color: #e0f2fe;
        color: #0369a1;
    }

    QPushButton[current="true"]:hover {
        background-color: #cfe8fc;
    }
"""


# shared by the popups and the emoji picker

def show_below(window, anchor):

    # puts a popup window just under the anchor widget and shows it
    position = anchor.mapToGlobal(anchor.rect().bottomLeft())

    window.adjustSize()

    window.move(position.x(), position.y() + 2)

    window.show()


class HoverFrame(QFrame):
    # small frame that tells us when the mouse enters / leaves it
    # (replaces the old monkey-patching of enterEvent / leaveEvent)

    entered = pyqtSignal()
    left = pyqtSignal()

    def enterEvent(self, event):

        self.entered.emit()

        super().enterEvent(event)

    def leaveEvent(self, event):

        self.left.emit()

        super().leaveEvent(event)

    def hideEvent(self, event):

        # if the popup gets hidden while the mouse is on it,
        # leaveEvent never fires, so we report it here
        self.left.emit()

        super().hideEvent(event)


class Pages(QObject):
    # shared page data: the page button, its popup and the sidebar all read from here
    changed = pyqtSignal()

    def __init__(self, first="Getting started"):
        super().__init__()
        self.items = [{"name": first, "emoji": "👋"}]
        self.current = 0

    @property
    def name(self):
        return self.items[self.current]["name"]

    @property
    def emoji(self):
        return self.items[self.current]["emoji"]

    def add(self, name, emoji="📄"):

        self.items.append({"name": name, "emoji": emoji})

        self.changed.emit()

    def select(self, index):

        self.current = index

        self.changed.emit()

    def rename(self, name):

        # live typing: a blank name is ignored so a page is never nameless
        if name.strip():
            self.items[self.current]["name"] = name.strip()

            self.changed.emit()

    def set_emoji(self, emoji):

        self.items[self.current]["emoji"] = emoji

        self.changed.emit()


class PageList(QWidget):
    # vertical list of pages, used by the hover popup and by the sidebar
    picked = pyqtSignal()

    def __init__(self, pages):
        super().__init__()
        self.pages = pages

        self.rows = QVBoxLayout(self)
        self.rows.setContentsMargins(0, 0, 0, 0)
        self.rows.setSpacing(3)

        self.refresh()

        pages.changed.connect(self.refresh)

    def refresh(self):

        # rebuild all the rows, there are only a few
        while self.rows.count():
            old = self.rows.takeAt(0).widget()

            old.setParent(None)

            old.deleteLater()

        for i, page in enumerate(self.pages.items):

            row = QPushButton(f"{page['emoji']}  {page['name']}")
            row.setProperty("current", i == self.pages.current)
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            row.setStyleSheet(ROW_STYLE)
            row.clicked.connect(lambda checked=False, i=i: self.pick(i))

            self.rows.addWidget(row)

    def pick(self, index):

        self.pages.select(index)

        self.picked.emit()


class PagesPopup(HoverFrame):
    # the floating window with the list of pages
    # (hover popup of the page button and of the sidebar button)

    def __init__(self, parent, pages):

        # pop_up1
        # ToolTip type instead of Popup: a Popup grabs the mouse, which
        # breaks hover detection and swallows the click on the button
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)

        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # needed so the rounded corners are actually transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setStyleSheet(POPUP_STYLE)

        self.setMinimumWidth(200)

        # popup ka layouttt

        popup_layout = QVBoxLayout(self)
        popup_layout.setContentsMargins(6, 6, 6, 6)

        # popup options

        self.page_list = PageList(pages)

        # all other options will be added here.
        # later this can contain:
        # - Pages
        # - TODOs
        # - Recent pages
        # - Sub-pages
        # - etc.

        popup_layout.addWidget(self.page_list)

        self.page_list.picked.connect(self.hide)


class HoverPopup(QObject):
    # shows the popup under the anchor after hovering it and hides it again
    # once the mouse is on neither of them (page button + sidebar button use it)

    def __init__(self, anchor, popup, can_show=lambda: True):
        super().__init__(anchor)
        self.anchor = anchor
        self.popup = popup
        self.can_show = can_show
        self.mouse_over_button = False
        self.mouse_over_popup = False

        # shows the popup 100 ms after hovering
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.setInterval(150)
        self.hover_timer.timeout.connect(self.show_popup)

        # small delay before hiding, so the mouse can cross the gap
        # between the button and the popup without closing it
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.setInterval(150)
        self.hide_timer.timeout.connect(self.check_popup)

        # popup mouse events (connected once here)😢 regretting things for some reason

        anchor.installEventFilter(self)
        popup.entered.connect(self.popup_enter)
        popup.left.connect(self.popup_leave)

    # 🐁 events lol

    def eventFilter(self, obj, event):

        if event.type() == QEvent.Type.Enter:

            self.mouse_over_button = True

            # coming back from the popup / gap, cancel any pending hide
            self.hide_timer.stop()

            self.hover_timer.start()

        elif event.type() == QEvent.Type.Leave:

            self.mouse_over_button = False

            self.hover_timer.stop()

            # not hiding instantly, check_popup runs after a short delay
            self.hide_timer.start()

        return super().eventFilter(obj, event)

    # popup mouse events

    def popup_enter(self):

        self.mouse_over_popup = True

        self.hover_timer.stop()

        self.hide_timer.stop()

    def popup_leave(self):

        self.mouse_over_popup = False

        self.hide_timer.start()

    def check_popup(self):

        if not self.mouse_over_button and not self.mouse_over_popup:
            self.popup.hide()

    # popup event

    def show_popup(self):

        # no popup while renaming, while the picker is open,
        # or if it is already showing
        if self.popup.isVisible() or not self.can_show():
            return

        show_below(self.popup, self.anchor)


class PageButton(QWidget):
    def __init__(self, pages):
        super().__init__()
        self.pages = pages
        self.setObjectName("pill")

        # stays only as wide as its contents, never stretches
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        # emoji + name look like ONE button: this widget draws the hover highlight
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        self.setStyleSheet("""
            #pill {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
            }

            #pill:hover {
                background-color: #eeeeee;
                border: 1px solid #cccccc;
            }
        """)

        # layouttttttt 😢 regretting things for some reason
        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)

        # emoji button (click = emoji picker)

        self.emoji_button = QPushButton(self.pages.emoji)
        self.emoji_button.setFixedSize(32, 32)
        self.emoji_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.emoji_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                font-size: 18px;
            }

            QPushButton:pressed {
                background-color: #e2e2e2;
            }
        """)

        self.emoji_button.clicked.connect(self.show_emoji_picker)

        layout.addWidget(self.emoji_button)

        # button jo main h (click = rename popup)

        self.button = QPushButton(self.pages.name)
        self.button.setFixedSize(200, 32)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                text-align: left;
                font-size: 14px;
            }

            QPushButton:pressed {
                background-color: #e2e2e2;
            }
        """)

        layout.addWidget(self.button)

        self.button.clicked.connect(self.start_rename)

        # rename popup, opens under the button
        # (same window type as the emoji picker: closes when you click outside)

        self.rename_popup = QFrame(self, Qt.WindowType.Popup)

        self.rename_popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.rename_popup.setStyleSheet(POPUP_STYLE)

        rename_layout = QVBoxLayout(self.rename_popup)
        rename_layout.setContentsMargins(6, 6, 6, 6)

        # rename box
        #addding the live changing while typing of page name function
        self.rename_box = QLineEdit()
        self.rename_box.textChanged.connect(self.pages.rename)#conencted the txt to changing signal
        self.rename_box.returnPressed.connect(self.rename_popup.hide)
        self.rename_box.setFixedSize(200, 32)

        self.rename_box.setStyleSheet("""
            QLineEdit {
                background-color: #eeeeee;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
            }
        """)

        rename_layout.addWidget(self.rename_box)

        # emoji picker

        self.emoji_picker = QFrame(self, Qt.WindowType.Popup)

        self.emoji_picker.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.emoji_picker.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
                border-radius: 8px;
            }

            QPushButton {
                background-color: transparent;
                border:none ;
                border-radius: 6px;
                font-size: 20px;
                padding: 5px;
            }

            QPushButton:hover {
                background-color: #eeeeee;
                border: 1px solid #cccccc;
            }
        """)

        emoji_layout = QHBoxLayout(self.emoji_picker)
        emoji_layout.setContentsMargins(6, 6, 6, 6)

        emojis = [
            "😀", "😂", "😍", "😎",
            "🔥", "🚀", "⭐", "❤️",
            "🎯", "💻", "📚", "🎨"
        ]

        for emoji in emojis:

            emoji_button = QPushButton(emoji)

            emoji_button.clicked.connect(lambda checked=False, e=emoji: self.change_emoji(e))

            emoji_layout.addWidget(emoji_button)

        # hover popup with the list of pages

        self.popup = PagesPopup(self, self.pages)

        self.hover = HoverPopup(self, self.popup, lambda: not (self.rename_popup.isVisible() or self.emoji_picker.isVisible()))

        # keeps the emoji / name on the button up to date
        self.pages.changed.connect(self.refresh)

    def refresh(self):

        self.emoji_button.setText(self.pages.emoji)

        self.button.setText(self.pages.name)

    # rename event

    def start_rename(self):

        self.popup.hide()

        self.rename_box.setText(self.pages.name)

        show_below(self.rename_popup, self)

        self.rename_box.setFocus()

        self.rename_box.selectAll()

    # emoji picker event

    def show_emoji_picker(self):

        self.popup.hide()

        show_below(self.emoji_picker, self.emoji_button)

    # change emoji

    def change_emoji(self, emoji):

        self.pages.set_emoji(emoji)

        self.emoji_picker.hide()