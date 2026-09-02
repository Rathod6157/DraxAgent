from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
)

from PySide6.QtCore import (
    Qt,
    Signal,
    QPropertyAnimation,
    QEasingCurve,
)

import widgets.theme as theme


class InputBar(QWidget):

    send_clicked = Signal(str)

    def __init__(self):
        super().__init__()

        self._build_ui()
        self._connect_signals()
        self._setup_animations()

    # ============================================================
    # UI
    # ============================================================

    def _build_ui(self):

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            18,
            10,
            18,
            18
        )

        layout.setSpacing(12)

        # --------------------------------------------------------
        # Input
        # --------------------------------------------------------

        self.input = QLineEdit()

        self.input.setPlaceholderText(
            "Talk to Drax..."
        )

        self.input.setMinimumHeight(52)

        self.input.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.input.setClearButtonEnabled(False)

        self.input.setStyleSheet(f"""
            QLineEdit {{
                background: {theme.INPUT_BACKGROUND};
                color: {theme.INPUT_TEXT};

                border: 1px solid {theme.INPUT_BORDER};
                border-radius: 18px;

                padding-left: 18px;
                padding-right: 18px;

                font-size: {theme.CHAT_SIZE}px;
                selection-background-color: {theme.ACCENT};
            }}

            QLineEdit:hover {{
                border: 1px solid {theme.INPUT_FOCUS};
            }}

            QLineEdit:focus {{
                border: 2px solid {theme.INPUT_FOCUS};
                padding-left: 17px;
                padding-right: 17px;
            }}
        """)

        # --------------------------------------------------------
        # Send button
        # --------------------------------------------------------

        self.send = QPushButton("➜")

        self.send.setFixedSize(
            52,
            52
        )

        self.send.setCursor(
            Qt.PointingHandCursor
        )

        self.send.setFocusPolicy(
            Qt.NoFocus
        )

        self.send.setStyleSheet(f"""
            QPushButton {{
                background: {theme.BUTTON_BACKGROUND};
                color: {theme.BUTTON_TEXT};

                border: none;
                border-radius: 26px;

                font-size: 21px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background: {theme.BUTTON_HOVER};
            }}

            QPushButton:pressed {{
                background: {theme.ACCENT};
            }}

            QPushButton:disabled {{
                background: {theme.INPUT_BORDER};
                color: {theme.TEXT_MUTED};
            }}
        """)

        layout.addWidget(
            self.input,
            1
        )

        layout.addWidget(
            self.send
        )

    # ============================================================
    # SIGNALS
    # ============================================================

    def _connect_signals(self):

        self.input.returnPressed.connect(
            self.send_message
        )

        self.send.clicked.connect(
            self.send_message
        )

        self.input.textChanged.connect(
            self._update_send_state
        )

        self._update_send_state()

    # ============================================================
    # ANIMATION
    # ============================================================

    def _setup_animations(self):

        self.send_animation = QPropertyAnimation(
            self.send,
            b"geometry",
            self
        )

        self.send_animation.setDuration(
            120
        )

        self.send_animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

    # ============================================================
    # SEND STATE
    # ============================================================

    def _update_send_state(self):

        has_text = bool(
            self.input.text().strip()
        )

        self.send.setEnabled(
            has_text
        )

    # ============================================================
    # SEND
    # ============================================================

    def send_message(self):

        text = self.input.text().strip()

        if not text:
            return

        self.send_clicked.emit(
            text
        )

        self.input.clear()

        self.input.setFocus()

    # ============================================================
    # PUBLIC HELPERS
    # ============================================================

    def set_enabled(
        self,
        enabled
    ):

        self.input.setEnabled(
            enabled
        )

        self.send.setEnabled(
            enabled and bool(
                self.input.text().strip()
            )
        )

    def focus_input(self):

        self.input.setFocus()