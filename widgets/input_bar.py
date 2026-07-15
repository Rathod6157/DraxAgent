from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)

from PySide6.QtCore import Signal

import widgets.theme as theme

class InputBar(QWidget):

    send_clicked = Signal(str)

    def __init__(self):
        super().__init__()

        self.build_ui()
        
    def build_ui(self):

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            18,
            10,
            18,
            18
        )

        layout.setSpacing(12)
        self.input = QLineEdit()

        self.input.setPlaceholderText(
            "Talk to Drax..."
        )

        self.input.returnPressed.connect(
            self.send_message
        )
        self.send = QPushButton("➜")

        self.send.clicked.connect(
            self.send_message
        )
        layout.addWidget(
            self.input,
            1
        )

        layout.addWidget(
            self.send
        )
        self.input.setStyleSheet(f"""
        QLineEdit{{
            background:{theme.INPUT_BACKGROUND};
            color:{theme.TEXT};
            border:2px solid transparent;
            border-radius:18px;
            padding:14px;
            font-size:14px;
        }}

        QLineEdit:focus{{
            border:2px solid {theme.ACCENT};
        }}
        """)
            
        self.send.setFixedSize(
            52,
            52
        )

        self.send.setStyleSheet(f"""
        QPushButton{{
            background:{theme.ACCENT};
            color:white;
            border:none;
            border-radius:26px;
            font-size:18px;
            font-weight:bold;
        }}

        QPushButton:hover{{
            background:{theme.ACCENT_HOVER};
        }}
        """)
        
    def send_message(self):

        text = self.input.text().strip()

        if not text:
            return

        self.send_clicked.emit(text)

        self.input.clear()