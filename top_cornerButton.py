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
    pyqtSignal
)

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


class PageButton(QWidget):
    name_changed = pyqtSignal(str)

    def __init__(self, name="Getting started"):
        super().__init__()
        self.name = name
        self.emoji = "👋"
        self.mouse_over_button = False
        self.mouse_over_popup = False
        self.renaming = False

        # stays only as wide as its contents, never stretches
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

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

        # layouttttttt 😢 regretting things for some reason
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        # emoji button

        self.emoji_button = QPushButton(self.emoji)
        self.emoji_button.setFixedSize(32, 32)
        self.emoji_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.emoji_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                font-size: 18px;
            }

            QPushButton:hover {
                background-color: #eeeeee;
                border:1px solid #cccccc;
            }

            QPushButton:pressed {
                background-color: #e2e2e2;
            }
        """)

        self.emoji_button.clicked.connect(self.show_emoji_picker)

        layout.addWidget(self.emoji_button)

        # button jo main h

        self.button = QPushButton(self.name)
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

            QPushButton:hover {
                background-color: #eeeeee;
                border: 2px solid #cccccc;
            }

            QPushButton:pressed {
                background-color: #eeeeee;
            }
        """)

        layout.addWidget(self.button)

        self.button.clicked.connect(self.start_rename)

        # rename box
        #addding the live changing while typing of page name function
        self.rename_box = QLineEdit()
        self.rename_box.textChanged.connect(self.name_changed)#conencted the txt to changing signal
        self.rename_box.setFixedSize(200, 32)

        self.rename_box.hide()

        self.rename_box.setStyleSheet("""
            QLineEdit {
                background-color: #eeeeee;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
            }
        """)

        layout.addWidget(self.rename_box)

        self.rename_box.editingFinished.connect(self.finish_rename)

        # pop_up1
        # ToolTip type instead of Popup: a Popup grabs the mouse, which
        # breaks hover detection and swallows the click on the button

        self.popup = HoverFrame(self, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)

        self.popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # needed so the rounded corners are actually transparent
        self.popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.popup.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dddddd;
                border-radius: 8px;
            }
        """)

        # popup mouse events (connected once here)😢 regretting things for some reason

        self.popup.entered.connect(self.popup_enter)
        self.popup.left.connect(self.popup_leave)

        # popup ka layouttt

        popup_layout = QVBoxLayout(self.popup)
        popup_layout.setContentsMargins(6, 6, 6, 6)
        popup_layout.setSpacing(3)

        # popup options

        option1 = QPushButton("more to be added")
        option1.setCursor(Qt.CursorShape.PointingHandCursor)

        option1.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 7px 12px;
                text-align: left;
                font-size: 13px;
            }

            QPushButton:hover {
                background-color: #eeeeee;
            }

            QPushButton:pressed {
                background-color: #e2e2e2;
            }
        """)

        # all other options will be added here.
        # later this can contain:
        # - Pages
        # - TODOs
        # - Recent pages
        # - Sub-pages
        # - etc.

        popup_layout.addWidget(option1)

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

    # 🐁 events lol

    def enterEvent(self, event):

        self.mouse_over_button = True

        # coming back from the popup / gap, cancel any pending hide
        self.hide_timer.stop()

        self.hover_timer.start()

        super().enterEvent(event)

    def leaveEvent(self, event):

        self.mouse_over_button = False

        self.hover_timer.stop()

        # not hiding instantly, check_popup runs after a short delay
        self.hide_timer.start()

        super().leaveEvent(event)

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

    # rename event

    def start_rename(self):

        self.renaming = True

        self.hover_timer.stop()

        self.popup.hide()

        self.button.hide()

        self.rename_box.setText(self.name)

        self.rename_box.show()

        self.rename_box.setFocus()

        self.rename_box.selectAll()

    def finish_rename(self):

        # editingFinished can fire twice (Enter, then focus loss when hidden)
        if not self.renaming:
            return

        self.renaming = False

        new_name = self.rename_box.text().strip()

        if new_name:
            self.name = new_name

            self.button.setText(self.name)

        # live typing may have sent a blank / half name, so send the real one
        self.name_changed.emit(self.name)

        self.rename_box.hide()

        self.button.show()

    # shared by the popup and the emoji picker

    def show_below(self, window, anchor):

        # puts a popup window just under the anchor widget and shows it
        position = anchor.mapToGlobal(anchor.rect().bottomLeft())

        window.adjustSize()

        window.move(position.x(), position.y() + 2)

        window.show()

    # emoji picker event

    def show_emoji_picker(self):

        self.hover_timer.stop()

        self.popup.hide()

        self.show_below(self.emoji_picker, self.emoji_button)

    # change emoji

    def change_emoji(self, emoji):

        self.emoji = emoji

        self.emoji_button.setText(self.emoji)

        self.emoji_picker.hide()

    # popup event

    def show_popup(self):

        # no popup while renaming, while the picker is open,
        # or if it is already showing
        if not self.button.isVisible():
            return

        if self.emoji_picker.isVisible() or self.popup.isVisible():
            return

        self.show_below(self.popup, self)