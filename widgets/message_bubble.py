from datetime import datetime

from PySide6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
)

from widgets import theme

from PySide6.QtCore import QTimer


class MessageBubble(QWidget):

    def __init__(
        self,
        text,
        sender="drax",
        timestamp=None,
        message_type="normal"
    ):
        super().__init__()

        self.sender = sender
        self.message_type = message_type
        self.text = text

        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M")

        self.timestamp = timestamp

        self.build_ui()
        
    def build_ui(self):

        outer = QHBoxLayout(self)

        outer.setContentsMargins(
            18,
            8,
            18,
            8
        )

        outer.setSpacing(0)


        self.container = QWidget()

        self.container.setMinimumWidth(0)

        self.container.setMaximumSize(
            theme.MAX_BUBBLE_WIDTH,
            16777215
        )

        


        bubble_layout = QVBoxLayout(self.container)

        bubble_layout.setContentsMargins(
            18,
            14,
            18,
            10
        )

        bubble_layout.setSpacing(8)


        self.message = QLabel(self.text)

        self.message.setWordWrap(True)

        self.message.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        self.message.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )


        self.time = QLabel(self.timestamp)

        self.time.setAlignment(Qt.AlignRight)


        bubble_layout.addWidget(self.message)

        bubble_layout.addWidget(self.time)
        # ------------------------
        # Styling
        # ------------------------

        self.time.setStyleSheet(f"""
            color:{theme.TEXT_MUTED};
            font-size:{theme.TIMESTAMP_SIZE}px;
        """)


        if self.sender == "user":

            self.container.setStyleSheet(f"""
                background:{theme.USER_BUBBLE};
                border-radius:{theme.BUBBLE_RADIUS}px;
            """)

            self.message.setStyleSheet(f"""
                color:{theme.USER_TEXT};
                font-size:{theme.CHAT_SIZE}px;
            """)

            outer.addStretch()

            outer.addWidget(self.container)


        else:

            self.container.setStyleSheet(f"""
                background:{theme.DRAX_BUBBLE};
                border-radius:{theme.BUBBLE_RADIUS}px;
            """)

            self.message.setStyleSheet(f"""
                color:{theme.DRAX_TEXT};
                font-size:{theme.CHAT_SIZE}px;
            """)

            outer.addWidget(self.container)

            outer.addStretch()
            
            
            #QTimer.singleShot(
            #    0,
            #    self.start_animation
            #)
            
            
    def set_text(self, text):

        self.text = text

        self.message.setText(text)


    def set_timestamp(self, timestamp):

        self.timestamp = timestamp

        self.time.setText(timestamp)
        
    
    def start_animation(self):

        start = self.pos() + QPoint(0, 12)

        end = self.pos()

        self.move(start)

        self.anim = QPropertyAnimation(
            self,
            b"pos"
        )

        self.anim.setStartValue(start)

        self.anim.setEndValue(end)

        self.anim.setDuration(180)

        self.anim.setEasingCurve(
            QEasingCurve.OutCubic
        )

        self.anim.start()    