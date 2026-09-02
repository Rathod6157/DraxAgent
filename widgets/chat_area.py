from datetime import datetime
import random

from PySide6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QGraphicsOpacityEffect,
    QSizePolicy,
)

from widgets.message_bubble import MessageBubble
import widgets.theme as theme


class ChatArea(QWidget):
    """
    DraxAgent conversation surface.

    Responsibilities:
        - Centered conversation column
        - Responsive conversation width
        - Full-width message rows
        - Stable left/right message alignment
        - Predictable scrolling
        - Welcome message
        - Thinking indicator
        - Lightweight animations

    Layout:

        FULL WINDOW
        ---------------------------------------------------------

                    CENTERED CHAT COLUMN

              Drax message
                                      User message

              Drax message
                                      User message

              Thinking...

        ---------------------------------------------------------

    ChatArea owns positioning.
    MessageBubble owns the visual bubble.
    """

    def __init__(self):
        super().__init__()

        self.welcome_bubble = None
        self.typing = None

        self.animations = []

        self.typing_animation = None
        self.typing_effect = None

        self._scroll_pending = False

        self.build_ui()

        QTimer.singleShot(
            0,
            self.show_welcome
        )

    # ============================================================
    # MAIN UI
    # ============================================================

    def build_ui(self):

        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(
            0
        )

        # --------------------------------------------------------
        # Scroll area
        # --------------------------------------------------------

        self.scroll = QScrollArea()

        self.scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.scroll.setWidget(
            self._create_scroll_container()
        )

        self.scroll.verticalScrollBar().setSingleStep(
            theme.SCROLL_SINGLE_STEP
        )

        # --------------------------------------------------------
        # Scrollbar
        # --------------------------------------------------------

        self.scroll.setStyleSheet(
            f"""
            QScrollArea {{
                background: {theme.CHAT_BACKGROUND};
                border: none;
            }}

            QScrollArea > QWidget > QWidget {{
                background: {theme.CHAT_BACKGROUND};
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 4px 2px 4px 0;
            }}

            QScrollBar::handle:vertical {{
                background: #3A3E48;
                border-radius: 4px;
                min-height: 42px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: #505562;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            """
        )

        root.addWidget(
            self.scroll
        )

    # ============================================================
    # SCROLL CONTAINER
    # ============================================================

    def _create_scroll_container(self):

        self.container = QWidget()

        self.container.setObjectName(
            "chatScrollContainer"
        )

        self.container.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.container.setStyleSheet(
            f"""
            QWidget#chatScrollContainer {{
                background: {theme.CHAT_BACKGROUND};
            }}
            """
        )

        self.container_layout = QHBoxLayout(
            self.container
        )

        self.container_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.container_layout.setSpacing(
            0
        )

        # --------------------------------------------------------
        # Center conversation
        # --------------------------------------------------------

        self.conversation = QWidget()

        self.conversation.setObjectName(
            "conversationColumn"
        )

        self.conversation.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Preferred
        )

        self.conversation.setMinimumWidth(
            0
        )

        self.conversation.setMaximumWidth(
            getattr(
                theme,
                "CONVERSATION_MAX_WIDTH",
                1180
            )
        )

        self.conversation.setStyleSheet(
            """
            QWidget#conversationColumn {
                background: transparent;
            }
            """
        )

        self.messages = QVBoxLayout(
            self.conversation
        )

        self.messages.setContentsMargins(
            getattr(
                theme,
                "CONVERSATION_SIDE_PADDING",
                28
            ),
            16,
            getattr(
                theme,
                "CONVERSATION_SIDE_PADDING",
                28
            ),
            24
        )

        self.messages.setSpacing(
            theme.CHAT_SPACING
        )

        self.messages.addStretch(
            1
        )

        # --------------------------------------------------------
        # Put conversation in center.
        #
        # IMPORTANT:
        # We do NOT use left/right stretch widgets here.
        # Instead, the conversation width is explicitly synced
        # to the available viewport width.
        # --------------------------------------------------------

        self.container_layout.addWidget(
            self.conversation,
            0,
            Qt.AlignHCenter
        )

        # Initial width.
        QTimer.singleShot(
            0,
            self._sync_conversation_width
        )

        return self.container

    # ============================================================
    # RESPONSIVE CONVERSATION WIDTH
    # ============================================================

    def _sync_conversation_width(self):

        if not hasattr(
            self,
            "container"
        ):
            return

        if not hasattr(
            self,
            "conversation"
        ):
            return

        available_width = (
            self.container.width()
        )

        if available_width <= 0:

            available_width = (
                self.scroll.viewport().width()
            )

        if available_width <= 0:
            return

        # --------------------------------------------------------
        # Horizontal breathing room.
        #
        # We leave a comfortable margin on both sides,
        # but allow the chat column to become much wider on
        # large/maximized windows.
        # --------------------------------------------------------

        outer_margin = 56

        target_width = max(
            320,
            available_width - outer_margin
        )

        maximum_width = getattr(
            theme,
            "CONVERSATION_MAX_WIDTH",
            1180
        )

        target_width = min(
            target_width,
            maximum_width
        )

        self.conversation.setFixedWidth(
            int(target_width)
        )

        self.conversation.updateGeometry()

        self._refresh_message_rows()

    # ============================================================
    # REFRESH MESSAGE ROWS
    # ============================================================

    def _refresh_message_rows(self):

        if not hasattr(
            self,
            "messages"
        ):
            return

        for index in range(
            self.messages.count() - 1
        ):

            item = self.messages.itemAt(
                index
            )

            widget = item.widget()

            if widget is None:
                continue

            widget.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Preferred
            )

            widget.updateGeometry()

            # ----------------------------------------------------
            # Give normal Drax messages more breathing room.
            #
            # This prevents a normal response from becoming
            # something like:
            #
            # "Hello Harshith. I see you are
            # working on my code in Visual
            # Studio Code..."
            #
            # just because the bubble's natural size hint
            # happened to be small.
            # ----------------------------------------------------

            if (
                hasattr(widget, "sender")
                and widget.sender == "drax"
                and getattr(
                    widget,
                    "message_type",
                    "normal"
                ) not in (
                    "welcome",
                    "status",
                )
            ):

                if hasattr(
                    widget,
                    "container"
                ):

                    current_width = (
                        widget.container.width()
                    )

                    target_width = min(
                        620,
                        max(
                            460,
                            current_width
                        )
                    )

                    widget.container.setMinimumWidth(
                        target_width
                    )

                    widget.container.setMaximumWidth(
                        min(
                            getattr(
                                theme,
                                "MAX_BUBBLE_WIDTH",
                                720
                            ),
                            720
                        )
                    )

            widget.adjustSize()

    # ============================================================
    # RESIZE
    # ============================================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
        )

        QTimer.singleShot(
            0,
            self._sync_conversation_width
        )

    # ============================================================
    # MESSAGE INSERTION
    # ============================================================

    def _insert_message_widget(
        self,
        widget
    ):

        if widget is None:
            return

        # --------------------------------------------------------
        # The MessageBubble itself must fill the entire
        # conversation column.
        #
        # This gives its internal layout a real left/right
        # surface to align against.
        # --------------------------------------------------------

        widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        self.messages.insertWidget(
            self.messages.count() - 1,
            widget
        )

        # Force the row to immediately acknowledge the
        # full conversation width.
        widget.setMinimumWidth(
            0
        )

        widget.updateGeometry()

        QTimer.singleShot(
            0,
            self._refresh_message_rows
        )

    # ============================================================
    # FADE IN
    # ============================================================

    def fade_in(
        self,
        widget,
        duration=160
    ):

        if widget is None:
            return

        effect = QGraphicsOpacityEffect(
            widget
        )

        effect.setOpacity(
            0.0
        )

        widget.setGraphicsEffect(
            effect
        )

        animation = QPropertyAnimation(
            effect,
            b"opacity",
            self
        )

        animation.setDuration(
            duration
        )

        animation.setStartValue(
            0.0
        )

        animation.setEndValue(
            1.0
        )

        animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        self.animations.append(
            animation
        )

        def finish():

            if animation in self.animations:

                self.animations.remove(
                    animation
                )

            effect.setOpacity(
                1.0
            )

        animation.finished.connect(
            finish
        )

        animation.start()

    # ============================================================
    # REMOVE WIDGET
    # ============================================================

    def _remove_widget(
        self,
        widget
    ):

        if widget is None:
            return

        widget.setGraphicsEffect(
            None
        )

        widget.hide()

        widget.deleteLater()

    # ============================================================
    # SCROLL
    # ============================================================

    def scroll_to_bottom(
        self,
        delay=0
    ):

        if self._scroll_pending:
            return

        self._scroll_pending = True

        def perform():

            self._scroll_pending = False

            scrollbar = (
                self.scroll.verticalScrollBar()
            )

            scrollbar.setValue(
                scrollbar.maximum()
            )

        QTimer.singleShot(
            delay,
            perform
        )

    # ============================================================
    # WELCOME MESSAGE
    # ============================================================

    def show_welcome(self):

        if self.welcome_bubble is not None:

            self._remove_widget(
                self.welcome_bubble
            )

            self.welcome_bubble = None

        hour = datetime.now().hour

        if 5 <= hour < 12:

            greeting = (
                "Good morning."
            )

        elif 12 <= hour < 17:

            greeting = (
                "Hey, good afternoon."
            )

        elif 17 <= hour < 22:

            greeting = (
                "Good evening."
            )

        else:

            greeting = (
                "Still up?"
            )

        suggestions = [
            "• What's on my screen?",
            "• Open Chrome",
            "• Check what's running",
            "• Click something on screen",
        ]

        alternate_suggestions = [
            "• What's on my screen?",
            "• What am I doing?",
            "• Open Chrome",
            "• Check what's running",
        ]

        if random.choice(
            [True, False]
        ):

            suggestions = (
                alternate_suggestions
            )

        text = (
            f"{greeting}\n\n"
            "I'm ready.\n\n"
            "You can ask me to:\n"
            f"{chr(10).join(suggestions)}"
        )

        self.welcome_bubble = MessageBubble(
            text=text,
            sender="drax",
            message_type="welcome"
        )

        self._insert_message_widget(
            self.welcome_bubble
        )

        self.fade_in(
            self.welcome_bubble,
            duration=220
        )

        self.scroll_to_bottom(
            delay=20
        )

    # ============================================================
    # HIDE WELCOME
    # ============================================================

    def hide_welcome(
        self,
        animated=False
    ):

        if self.welcome_bubble is None:
            return

        bubble = self.welcome_bubble

        self.welcome_bubble = None

        self._remove_widget(
            bubble
        )

    # ============================================================
    # ADD MESSAGE
    # ============================================================

    def add_message(
        self,
        text,
        sender="drax",
        message_type="normal"
    ):

        if text is None:
            return

        text = str(
            text
        )

        bubble = MessageBubble(
            text=text,
            sender=sender,
            message_type=message_type
        )

        self._insert_message_widget(
            bubble
        )

        self.fade_in(
            bubble,
            duration=150
        )

        self.scroll_to_bottom(
            delay=20
        )

        return bubble

    # ============================================================
    # USER MESSAGE
    # ============================================================

    def add_user_message(
        self,
        text
    ):

        self.hide_welcome(
            animated=False
        )

        bubble = self.add_message(
            text=text,
            sender="user"
        )

        self.scroll_to_bottom(
            delay=35
        )

        return bubble

    # ============================================================
    # DRAX MESSAGE
    # ============================================================

    def add_drax_message(
        self,
        text,
        message_type="normal"
    ):

        self.hide_typing()

        bubble = self.add_message(
            text=text,
            sender="drax",
            message_type=message_type
        )

        self.scroll_to_bottom(
            delay=35
        )

        return bubble

    # ============================================================
    # CLEAR CHAT
    # ============================================================

    def clear(self):

        self.hide_typing()

        self.hide_welcome(
            animated=False
        )

        while self.messages.count() > 1:

            item = self.messages.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:

                widget.setGraphicsEffect(
                    None
                )

                widget.deleteLater()

        self.welcome_bubble = None

        QTimer.singleShot(
            30,
            self.show_welcome
        )

    # ============================================================
    # THINKING INDICATOR
    # ============================================================

    def show_typing(self):

        self.hide_typing(
            animate=False
        )

        self.typing = MessageBubble(
            text="Drax is thinking...",
            sender="drax",
            message_type="status"
        )

        self._insert_message_widget(
            self.typing
        )

        self.typing_effect = (
            QGraphicsOpacityEffect(
                self.typing.message
            )
        )

        self.typing_effect.setOpacity(
            theme.THINKING_OPACITY_MIN
        )

        self.typing.message.setGraphicsEffect(
            self.typing_effect
        )

        self.typing_animation = (
            QPropertyAnimation(
                self.typing_effect,
                b"opacity",
                self
            )
        )

        self.typing_animation.setDuration(
            900
        )

        self.typing_animation.setStartValue(
            theme.THINKING_OPACITY_MIN
        )

        self.typing_animation.setEndValue(
            theme.THINKING_OPACITY_MAX
        )

        self.typing_animation.setEasingCurve(
            QEasingCurve.InOutSine
        )

        self.typing_animation.setLoopCount(
            -1
        )

        self.typing_animation.start()

        self.scroll_to_bottom(
            delay=20
        )

    # ============================================================
    # HIDE THINKING
    # ============================================================

    def hide_typing(
        self,
        animate=False
    ):

        if self.typing_animation is not None:

            self.typing_animation.stop()

            self.typing_animation.deleteLater()

            self.typing_animation = None

        if self.typing_effect is not None:

            self.typing_effect.setOpacity(
                1.0
            )

            self.typing_effect = None

        if self.typing is None:
            return

        bubble = self.typing

        self.typing = None

        if hasattr(
            bubble,
            "message"
        ):

            bubble.message.setGraphicsEffect(
                None
            )

        if animate:

            self.fade_out_and_remove(
                bubble,
                duration=120
            )

        else:

            self._remove_widget(
                bubble
            )

    # ============================================================
    # FADE OUT
    # ============================================================

    def fade_out_and_remove(
        self,
        widget,
        duration=120
    ):

        if widget is None:
            return

        effect = QGraphicsOpacityEffect(
            widget
        )

        effect.setOpacity(
            1.0
        )

        widget.setGraphicsEffect(
            effect
        )

        animation = QPropertyAnimation(
            effect,
            b"opacity",
            self
        )

        animation.setDuration(
            duration
        )

        animation.setStartValue(
            1.0
        )

        animation.setEndValue(
            0.0
        )

        animation.setEasingCurve(
            QEasingCurve.InCubic
        )

        self.animations.append(
            animation
        )

        def finish():

            if animation in self.animations:

                self.animations.remove(
                    animation
                )

            widget.setGraphicsEffect(
                None
            )

            widget.deleteLater()

        animation.finished.connect(
            finish
        )

        animation.start()

    # ============================================================
    # CLEANUP
    # ============================================================

    def closeEvent(
        self,
        event
    ):

        if self.typing_animation is not None:

            self.typing_animation.stop()

            self.typing_animation = None

        for animation in list(
            self.animations
        ):

            animation.stop()

        self.animations.clear()

        super().closeEvent(
            event
        )