from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
)

from PySide6.QtCore import (
    QTimer,
)

import widgets.theme as theme

class StatusBar(QWidget):

    def __init__(self):
        super().__init__()

        self.build_ui()

    def build_ui(self):

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            12,
            8,
            12,
            8
        )

        self.icon = QLabel("●")

        self.label = QLabel("")

        layout.addWidget(self.icon)

        layout.addWidget(self.label)

        layout.addStretch()

        self.setStyleSheet(f"""
        QWidget{{
            background:{theme.DRAX_BUBBLE};
            border-radius:12px;
        }}

        QLabel{{
            color:{theme.TEXT};
            font-size:13px;
        }}
        """)

        self.hide()
        self.dots = 1

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.animate
        )
        
    def show_message(
        self,
        text
    ):

        self.label.setText(text)

        self.show()

        self.dots = 1
        self.icon.setText("●")
        self.timer.start(350)
    
    def hide_message(self):

        self.timer.stop()

        self.hide()

        self.icon.setText("●")
    
    def animate(self):

        self.dots += 1

        if self.dots > 3:
            self.dots = 1

        self.icon.setText(
            "●" * self.dots
        )