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
        - Stable conversation layout
        - Responsive centered conversation column
        - Predictable scrolling
        - Safe message insertion/removal
        - Welcome message
        - Thinking indicator
        - Lightweight visual animations

    Important:
        This class does NOT perform any AI/network work.
        It only manages the GUI.
    """

    def __init__(self):
        super().__init__()

        self.welcome_bubble = None
        self.typing = None

        # Active opacity animations.
        self.animations = []

        # Thinking animation compatibility.
        self.typing_animation = None
        self.typing_effect = None

        # Scroll scheduling.
        self._scroll_timer = None
        self._scroll_generation = 0

        self.build_ui()

        # Wait until Qt has completed the initial layout pass.
        QTimer.singleShot(
            0,
            self.show_welcome
        )

    # ============================================================
    # UI
    # ============================================================

    def build_ui(self):
        root = QVBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(0)

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

        self.scroll.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.scroll.setStyleSheet(
            f"""
            QScrollArea {{
                background: {theme.CHAT_BACKGROUND};
                border: none;
            }}

            QScrollArea > QWidget {{
                background: {theme.CHAT_BACKGROUND};
                border: none;
            }}

            QScrollArea > QWidget > QWidget {{
                background: {theme.CHAT_BACKGROUND};
                border: none;
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

        self.container = self._create_message_container()

        self.scroll.setWidget(
            self.container
        )

        self.scroll.verticalScrollBar().setSingleStep(
            theme.SCROLL_SINGLE_STEP
        )

        root.addWidget(
            self.scroll
        )

    # ============================================================
    # MESSAGE CONTAINER
    # ============================================================

    def _create_message_container(self):
        """
        Creates the full-width scroll content.

        The actual conversation is kept centered inside the
        available width, while remaining responsive on smaller
        windows.
        """

        container = QWidget()

        container.setObjectName(
            "chatContainer"
        )

        container.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )

        container.setStyleSheet(
            f"""
            QWidget#chatContainer {{
                background: {theme.CHAT_BACKGROUND};
            }}
            """
        )

        outer = QHBoxLayout(
            container
        )

        outer.setContentsMargins(
            0,
            0,
            0,
            0
        )

        outer.setSpacing(0)

        # --------------------------------------------------------
        # Left breathing room
        # --------------------------------------------------------

        outer.addStretch(1)

        # --------------------------------------------------------
        # Responsive conversation column
        # --------------------------------------------------------

        self.conversation = QWidget()

        self.conversation.setObjectName(
            "conversationColumn"
        )

        self.conversation.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )

        # IMPORTANT:
        # Use the centralized theme value instead of a hardcoded
        # 820px limit.
        self.conversation.setMaximumWidth(
            theme.CONVERSATION_MAX_WIDTH
        )

        self.conversation.setStyleSheet(
            f"""
            QWidget#conversationColumn {{
                background: {theme.CHAT_BACKGROUND};
            }}
            """
        )

        self.messages = QVBoxLayout(
            self.conversation
        )

        self.messages.setContentsMargins(
            theme.CONVERSATION_SIDE_PADDING,
            18,
            theme.CONVERSATION_SIDE_PADDING,
            22
        )

        self.messages.setSpacing(
            theme.CHAT_SPACING
        )

        # --------------------------------------------------------
        # Bottom anchor
        # --------------------------------------------------------

        self.bottom_stretch_index = (
            self.messages.count()
        )

        self.messages.addStretch(
            1
        )

        outer.addWidget(
            self.conversation
        )

        # --------------------------------------------------------
        # Right breathing room
        # --------------------------------------------------------

        outer.addStretch(1)

        return container

    # ============================================================
    # MESSAGE INSERTION
    # ============================================================

    def _insert_message_widget(
        self,
        widget
    ):
        """
        Insert a message immediately before the bottom stretch.

        Existing messages are never repositioned manually.
        """

        if widget is None:
            return

        index = self.messages.count() - 1

        if index < 0:
            index = 0

        self.messages.insertWidget(
            index,
            widget
        )

        widget.show()

        widget.updateGeometry()
        self.conversation.updateGeometry()
        self.container.updateGeometry()

    # ============================================================
    # FADE IN
    # ============================================================

    def fade_in(
        self,
        widget,
        duration=150
    ):
        """
        Opacity-only entrance animation.

        No geometry or positional animation is used.
        """

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

            try:
                widget.setGraphicsEffect(
                    None
                )
            except RuntimeError:
                pass

        animation.finished.connect(
            finish
        )

        animation.start()

    # ============================================================
    # SAFE REMOVE
    # ============================================================

    def _remove_widget(
        self,
        widget
    ):
        """
        Remove a widget safely.

        No geometry animation is used.
        """

        if widget is None:
            return

        try:
            widget.setGraphicsEffect(
                None
            )
        except RuntimeError:
            return

        widget.hide()
        widget.deleteLater()

        self.conversation.updateGeometry()
        self.container.updateGeometry()

    # ============================================================
    # SCROLLING
    # ============================================================

    def scroll_to_bottom(
        self,
        delay=0
    ):
        """
        Scroll to the newest message after Qt has completed
        pending layout/geometry work.

        Multiple requests are coalesced.
        """

        self._scroll_generation += 1

        generation = (
            self._scroll_generation
        )

        if self._scroll_timer is not None:
            self._scroll_timer.stop()
            self._scroll_timer.deleteLater()
            self._scroll_timer = None

        def perform():
            if generation != self._scroll_generation:
                return

            self._scroll_timer = None

            scrollbar = (
                self.scroll.verticalScrollBar()
            )

            scrollbar.setValue(
                scrollbar.maximum()
            )

        timer = QTimer(
            self
        )

        timer.setSingleShot(
            True
        )

        timer.timeout.connect(
            perform
        )

        self._scroll_timer = timer

        timer.start(
            max(
                0,
                int(delay)
            )
        )

    # ============================================================
    # WELCOME
    # ============================================================

    def show_welcome(self):
        """
        Display the initial Drax greeting.
        """

        if self.welcome_bubble is not None:
            self._remove_widget(
                self.welcome_bubble
            )

            self.welcome_bubble = None

        hour = datetime.now().hour

        if 5 <= hour < 12:
            greeting = "Good morning."
        elif 12 <= hour < 17:
            greeting = "Hey, good afternoon."
        elif 17 <= hour < 22:
            greeting = "Good evening."
        else:
            greeting = "Still up?"

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
            suggestions = alternate_suggestions

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
            delay=30
        )

    # ============================================================
    # HIDE WELCOME
    # ============================================================

    def hide_welcome(
        self,
        animated=False
    ):
        """
        Remove the welcome bubble.

        'animated' remains for compatibility with gui.py.
        """

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
        """
        Create and insert a conversation bubble.
        """

        if text is None:
            return None

        text = str(
            text
        )

        if not text.strip():
            return None

        bubble = MessageBubble(
            text=text,
            sender=sender,
            message_type=message_type
        )

        self._insert_message_widget(
            bubble
        )

        self.scroll_to_bottom(
            delay=25
        )

        return bubble

    # ============================================================
    # USER MESSAGE
    # ============================================================

    def add_user_message(
        self,
        text
    ):
        """
        Add a user message.
        """

        self.hide_welcome(
            animated=False
        )

        bubble = self.add_message(
            text=text,
            sender="user"
        )

        self.scroll_to_bottom(
            delay=40
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
        """
        Add a Drax message.

        Removes the thinking indicator first.
        """

        self.hide_typing()

        bubble = self.add_message(
            text=text,
            sender="drax",
            message_type=message_type
        )

        self.scroll_to_bottom(
            delay=40
        )

        return bubble

    # ============================================================
    # CLEAR
    # ============================================================

    def clear(self):
        """
        Clear conversation history while preserving
        the conversation column and bottom anchor.
        """

        self.hide_typing()

        self.hide_welcome(
            animated=False
        )

        # Remove every actual message.
        while self.messages.count() > 1:
            item = self.messages.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:
                try:
                    widget.setGraphicsEffect(
                        None
                    )
                except RuntimeError:
                    pass

                widget.deleteLater()

        self.welcome_bubble = None

        self.conversation.updateGeometry()
        self.container.updateGeometry()

        QTimer.singleShot(
            30,
            self.show_welcome
        )

    # ============================================================
    # THINKING INDICATOR
    # ============================================================

    def show_typing(self):
        """
        Show the stable 'Drax is thinking...' bubble.

        The bubble itself does not move.
        """

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

        self.scroll_to_bottom(
            delay=25
        )

    # ============================================================
    # HIDE THINKING INDICATOR
    # ============================================================

    def hide_typing(
        self,
        animate=False
    ):
        """
        Remove the thinking indicator.

        'animate' remains for compatibility.
        """

        if self.typing is None:
            return

        bubble = self.typing

        self.typing = None

        self._remove_widget(
            bubble
        )

    # ============================================================
    # OPTIONAL FADE OUT
    # ============================================================

    def fade_out_and_remove(
        self,
        widget,
        duration=120
    ):
        """
        Optional helper for transient widgets.
        """

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

            try:
                widget.setGraphicsEffect(
                    None
                )
            except RuntimeError:
                return

            widget.deleteLater()

        animation.finished.connect(
            finish
        )

        animation.start()

    # ============================================================
    # RESIZE
    # ============================================================

    def resizeEvent(
        self,
        event
    ):
        """
        Keep the conversation centered and responsive.

        Large windows use the theme-defined maximum width.
        Smaller windows naturally consume the available width.
        """

        super().resizeEvent(
            event
        )

        self.container.updateGeometry()
        self.conversation.updateGeometry()

        QTimer.singleShot(
            0,
            lambda: self.scroll_to_bottom(
                delay=0
            )
        )

    # ============================================================
    # CLEANUP
    # ============================================================

    def closeEvent(
        self,
        event
    ):
        if self._scroll_timer is not None:
            self._scroll_timer.stop()
            self._scroll_timer = None

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