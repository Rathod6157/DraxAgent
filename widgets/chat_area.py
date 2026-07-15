from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QFrame,
)

from widgets.message_bubble import MessageBubble

import widgets.theme as theme

from PySide6.QtCore import (
    Qt,
    QTimer,
)

class ChatArea(QWidget):

    def __init__(self):
        super().__init__()

        self.build_ui()
        self.show_welcome()
    def build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.setSpacing(0)

        self.scroll = QScrollArea()
        
        self.scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.scroll.setStyleSheet(f"""
        QScrollArea {{
            background:{theme.CHAT_BACKGROUND};
            border:none;
        }}

        QWidget {{
            background:{theme.CHAT_BACKGROUND};
        }}
        """)

        self.scroll.setWidgetResizable(True)

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        
        self.scroll.verticalScrollBar().setSingleStep(18)
        
        self.container = QWidget()

        self.messages = QVBoxLayout(self.container)

        self.messages.setSpacing(14)

        self.messages.setContentsMargins(
            26,
            18,
            26,
            18
        )

        self.messages.addStretch()

        self.scroll.setWidget(self.container)

        layout.addWidget(self.scroll)
        
        
    def show_welcome(self):

        self.add_drax_message(
            message_type="welcome",
            text=
            "👋 Welcome back.\n\n"
            "Ready whenever you are.\n\n"
            "Try asking me to:\n"
            "• Open Chrome\n"
            "• Set a timer\n"
            "• Close Spotify\n"
            "• Check what's running"
        )
    
    def add_message(
        self,
        text,
        sender="drax",
        message_type="normal"
    ):

        bubble = MessageBubble(
            text=text,
            sender=sender,
            message_type=message_type
        )

        self.messages.insertWidget(
            self.messages.count() - 1,
            bubble
        )

        QTimer.singleShot(
            0,
            self.scroll_to_bottom
        )   
    def add_user_message(
        self,
        text
    ):
        self.add_message(
            text=text,
            sender="user"
        )
    def add_drax_message(
        self,
        text,
        message_type="normal"
    ):
        self.add_message(
            text=text,
            sender="drax",
            message_type=message_type
        )
        
    def clear(self):

        while self.messages.count() > 1:

            item = self.messages.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        QTimer.singleShot(
            0,
            self.show_welcome
        )
                
    def scroll_to_bottom(self):

        scrollbar = self.scroll.verticalScrollBar()

        scrollbar.setValue(
            scrollbar.maximum()
        )
        
    def show_typing(self):

        self.typing = MessageBubble(
            text="Drax is thinking...",
            sender="drax",
            message_type="status"
        )

        self.messages.insertWidget(
            self.messages.count() - 1,
            self.typing
        )

        self.scroll_to_bottom()
        
    def hide_typing(self):

        if hasattr(self, "typing"):

            self.typing.deleteLater()

            del self.typing