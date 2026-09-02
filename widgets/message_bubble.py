from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
)

import widgets.theme as theme


class MessageBubble(QWidget):
    """
    DraxAgent chat message widget.

    Responsibilities:
        - Render an individual chat message.
        - Render Drax branding.
        - Render timestamps.
        - Render the thinking/status state.
        - Give bubbles a comfortable, adaptive width.

    Layout responsibility:
        ChatArea owns the overall conversation column.

        MessageBubble owns the visual bubble inside that column.

    Important design rules:
        - This widget never animates its geometry.
        - Normal bubbles are wide enough to feel intentional.
        - Long messages may grow up to MAX_BUBBLE_WIDTH.
        - Short messages do not collapse into tiny floating islands.
        - Drax messages stay left aligned.
        - User messages stay right aligned.
    """

    # ------------------------------------------------------------
    # Bubble sizing
    # ------------------------------------------------------------

    # Comfortable minimum widths for normal conversation bubbles.
    # These prevent short messages such as "Hi" from becoming tiny.
    MIN_DRAX_BUBBLE_WIDTH = 300
    MIN_USER_BUBBLE_WIDTH = 150

    # Welcome card gets its own larger width.
    WELCOME_MIN_WIDTH = 520
    WELCOME_MAX_WIDTH = 680

    def __init__(
        self,
        text,
        sender="drax",
        timestamp=None,
        message_type="normal",
    ):
        super().__init__()

        self.sender = sender
        self.message_type = message_type
        self.text = str(text)

        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M")

        self.timestamp = timestamp

        self.build_ui()

    # ============================================================
    # UI
    # ============================================================

    def build_ui(self):
        """
        Build one complete conversation row.

        The MessageBubble itself expands to the available width
        supplied by ChatArea.

        The visual container is aligned left/right inside that row.
        """

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred,
        )

        outer = QHBoxLayout(self)

        outer.setContentsMargins(
            0,
            5,
            0,
            5,
        )

        outer.setSpacing(0)

        # --------------------------------------------------------
        # Visual bubble
        # --------------------------------------------------------

        self.container = QWidget()

        # --------------------------------------------------------
        # Bubble sizing
        # --------------------------------------------------------

        if self.message_type == "welcome":
            self.container.setMinimumWidth(
                self.WELCOME_MIN_WIDTH
            )

            self.container.setMaximumWidth(
                self.WELCOME_MAX_WIDTH
            )

            self.container.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Preferred,
            )

        elif self.message_type == "status":
            # Thinking indicator should remain compact.
            self.container.setMinimumWidth(210)

            self.container.setMaximumWidth(
                min(
                    theme.MAX_BUBBLE_WIDTH,
                    360,
                )
            )

            self.container.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Fixed,
            )

        elif self.sender == "user":
            # User bubbles should remain compact, but not microscopic.
            self.container.setMinimumWidth(
                self.MIN_USER_BUBBLE_WIDTH
            )

            self.container.setMaximumWidth(
                theme.MAX_BUBBLE_WIDTH
            )

            self.container.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Preferred,
            )

        else:
            # Drax gets a more substantial conversational width.
            self.container.setMinimumWidth(
                self.MIN_DRAX_BUBBLE_WIDTH
            )

            self.container.setMaximumWidth(
                theme.MAX_BUBBLE_WIDTH
            )

            self.container.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Preferred,
            )

        # --------------------------------------------------------
        # Bubble layout
        # --------------------------------------------------------

        bubble_layout = QVBoxLayout(
            self.container
        )

        bubble_layout.setContentsMargins(
            theme.BUBBLE_HORIZONTAL_PADDING + 2,
            theme.BUBBLE_VERTICAL_PADDING + 5,
            theme.BUBBLE_HORIZONTAL_PADDING + 2,
            theme.BUBBLE_VERTICAL_PADDING,
        )

        bubble_layout.setSpacing(6)

        # --------------------------------------------------------
        # STATUS / THINKING BUBBLE
        # --------------------------------------------------------

        if self.message_type == "status":
            self._build_status_bubble(
                outer,
                bubble_layout,
            )

            return

        # --------------------------------------------------------
        # DRAX BRANDING
        # --------------------------------------------------------

        if self.sender == "drax":
            branding_row = QHBoxLayout()

            branding_row.setContentsMargins(
                0,
                0,
                0,
                0,
            )

            branding_row.setSpacing(7)

            # ----------------------------------------------------
            # Logo
            # ----------------------------------------------------

            self.logo = QLabel()

            self.logo.setFixedSize(
                theme.LOGO_SMALL_SIZE,
                theme.LOGO_SMALL_SIZE,
            )

            self.logo.setScaledContents(True)

            logo_path = Path(
                theme.DRAX_ICON
            )

            if logo_path.exists():
                pixmap = QPixmap(
                    str(logo_path)
                )

                if not pixmap.isNull():
                    self.logo.setPixmap(
                        pixmap.scaled(
                            theme.LOGO_SMALL_SIZE,
                            theme.LOGO_SMALL_SIZE,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation,
                        )
                    )

            self.logo.setStyleSheet(
                """
                QLabel {
                    background: transparent;
                }
                """
            )

            # ----------------------------------------------------
            # Drax name
            # ----------------------------------------------------

            self.drax_label = QLabel(
                "Drax"
            )

            self.drax_label.setStyleSheet(
                f"""
                QLabel {{
                    color: {theme.TEXT_SECONDARY};
                    font-size: 11px;
                    font-weight: {theme.FONT_MEDIUM};
                    background: transparent;
                }}
                """
            )

            branding_row.addWidget(
                self.logo
            )

            branding_row.addWidget(
                self.drax_label
            )

            branding_row.addStretch()

            bubble_layout.addLayout(
                branding_row
            )

        # --------------------------------------------------------
        # MESSAGE TEXT
        # --------------------------------------------------------

        self.message = QLabel()

        self.message.setText(
            self.text
        )

        self.message.setWordWrap(
            True
        )

        self.message.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        self.message.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred,
        )

        # --------------------------------------------------------
        # TIMESTAMP
        # --------------------------------------------------------

        self.time = QLabel(
            self.timestamp
        )

        self.time.setAlignment(
            Qt.AlignRight
        )

        self.time.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Fixed,
        )

        self.time.setStyleSheet(
            f"""
            QLabel {{
                color: {theme.TIMESTAMP_COLOR};
                font-size: {theme.TIMESTAMP_SIZE}px;
                background: transparent;
            }}
            """
        )

        # --------------------------------------------------------
        # Add content
        # --------------------------------------------------------

        bubble_layout.addWidget(
            self.message
        )

        bubble_layout.addWidget(
            self.time
        )

        # --------------------------------------------------------
        # USER MESSAGE
        # --------------------------------------------------------

        if self.sender == "user":

            self.container.setStyleSheet(
                f"""
                QWidget {{
                    background: {theme.USER_BUBBLE};
                    border-radius: {theme.BUBBLE_RADIUS}px;
                }}
                """
            )

            self.message.setStyleSheet(
                f"""
                QLabel {{
                    color: {theme.USER_TEXT};
                    font-size: {theme.CHAT_SIZE}px;
                    background: transparent;
                }}
                """
            )

            # ----------------------------------------------------
            # Right aligned
            #
            # [                 USER BUBBLE]
            # ----------------------------------------------------

            outer.addStretch(
                1
            )

            outer.addWidget(
                self.container,
                0,
                Qt.AlignRight,
            )

        # --------------------------------------------------------
        # DRAX MESSAGE
        # --------------------------------------------------------

        else:

            self.container.setStyleSheet(
                f"""
                QWidget {{
                    background: {theme.DRAX_BUBBLE};
                    border-radius: {theme.BUBBLE_RADIUS}px;
                }}
                """
            )

            self.message.setStyleSheet(
                f"""
                QLabel {{
                    color: {theme.DRAX_TEXT};
                    font-size: {theme.CHAT_SIZE}px;
                    background: transparent;
                }}
                """
            )

            # ----------------------------------------------------
            # Left aligned
            #
            # [DRAX BUBBLE]
            # ----------------------------------------------------

            outer.addWidget(
                self.container,
                0,
                Qt.AlignLeft,
            )

            outer.addStretch(
                1
            )

        # --------------------------------------------------------
        # Let Qt calculate the actual content height.
        # --------------------------------------------------------

        self.container.adjustSize()
        self.adjustSize()

    # ============================================================
    # STATUS / THINKING
    # ============================================================

    def _build_status_bubble(
        self,
        outer,
        bubble_layout,
    ):
        """
        Build the stable Drax thinking indicator.

        The bubble itself never moves or animates.
        ChatArea may animate the opacity of the text.
        """

        self.status_text = QLabel(
            theme.THINKING_TEXT + "..."
        )

        # --------------------------------------------------------
        # Compatibility
        #
        # ChatArea expects:
        #
        #     typing.message
        #
        # So expose the same QLabel through .message.
        # --------------------------------------------------------

        self.message = self.status_text

        self.status_text.setAlignment(
            Qt.AlignLeft |
            Qt.AlignVCenter
        )

        self.status_text.setStyleSheet(
            f"""
            QLabel {{
                color: {theme.TEXT_SECONDARY};
                font-size: {theme.STATUS_SIZE}px;
                font-weight: {theme.FONT_MEDIUM};
                background: transparent;
            }}
            """
        )

        self.status_text.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        bubble_layout.addWidget(
            self.status_text
        )

        # --------------------------------------------------------
        # Status bubble appearance
        # --------------------------------------------------------

        self.container.setStyleSheet(
            f"""
            QWidget {{
                background: {theme.STATUS_BUBBLE};
                border-radius: {theme.BUBBLE_RADIUS}px;
            }}
            """
        )

        # --------------------------------------------------------
        # Left aligned
        # --------------------------------------------------------

        outer.addWidget(
            self.container,
            0,
            Qt.AlignLeft,
        )

        outer.addStretch(
            1
        )

        self.container.adjustSize()
        self.adjustSize()

    # ============================================================
    # TEXT
    # ============================================================

    def set_text(
        self,
        text,
    ):
        """
        Update the message text safely.
        """

        self.text = str(text)

        if hasattr(
            self,
            "message",
        ):
            self.message.setText(
                self.text
            )

            self.message.adjustSize()
            self.container.adjustSize()
            self.adjustSize()

    # ============================================================
    # THINKING TEXT
    # ============================================================

    def set_status_text(
        self,
        text,
    ):
        """
        Update the thinking indicator text.
        """

        if not hasattr(
            self,
            "status_text",
        ):
            return

        self.status_text.setText(
            str(text)
        )

        self.status_text.adjustSize()
        self.container.adjustSize()
        self.adjustSize()

    # ============================================================
    # TIMESTAMP
    # ============================================================

    def set_timestamp(
        self,
        timestamp,
    ):
        """
        Update the timestamp.
        """

        self.timestamp = timestamp

        if hasattr(
            self,
            "time",
        ):
            self.time.setText(
                timestamp
            )

    # ============================================================
    # CLEANUP
    # ============================================================

    def stop_animations(self):
        """
        Compatibility method.

        MessageBubble itself does not own animations.
        ChatArea owns thinking/appearance animations.
        """

        pass