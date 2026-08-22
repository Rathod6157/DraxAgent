import ctypes
import ctypes.wintypes

from PySide6.QtCore import (
    Qt,
    QObject,
    QThread,
    Signal,
    QTimer,
    QAbstractNativeEventFilter,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
    QParallelAnimationGroup,
)

from PySide6.QtGui import QCursor

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QFrame,
    QApplication,
    QGraphicsOpacityEffect,
)

import widgets.theme as theme

from brain.drax import drax


# ============================================================
# Windows Global Hotkey
# ============================================================

user32 = ctypes.windll.user32

WM_HOTKEY = 0x0312

MOD_CONTROL = 0x0002
VK_SPACE = 0x20

HOTKEY_ID = 9001


class GlobalHotkeyFilter(
    QAbstractNativeEventFilter
):

    def __init__(self, callback):

        super().__init__()

        self.callback = callback

        user32.RegisterHotKey(
            None,
            HOTKEY_ID,
            MOD_CONTROL,
            VK_SPACE
        )

    def nativeEventFilter(
        self,
        event_type,
        message
    ):

        if event_type == "windows_generic_MSG":

            msg = ctypes.wintypes.MSG.from_address(
                int(message)
            )

            if msg.message == WM_HOTKEY:

                if msg.wParam == HOTKEY_ID:

                    self.callback()

                    return True, 0

        return False, 0

    def unregister(self):

        user32.UnregisterHotKey(
            None,
            HOTKEY_ID
        )


# ============================================================
# AI Worker
# ============================================================

class SummonWorker(QObject):

    finished = Signal()
    response_ready = Signal(str)

    def __init__(
        self,
        command
    ):

        super().__init__()

        self.command = command

    def run(self):

        try:

            response = drax.chat(
                self.command
            )

            if isinstance(
                response,
                str
            ):

                response = response.strip()

                if response:

                    self.response_ready.emit(
                        response
                    )

            else:

                # Action commands may complete
                # without returning a text response.
                self.response_ready.emit(
                    "Done."
                )

        except Exception as error:

            self.response_ready.emit(
                f"Something went wrong: {error}"
            )

        finally:

            self.finished.emit()


# ============================================================
# Draggable Header
# ============================================================

class DragHeader(QFrame):

    def __init__(
        self,
        window
    ):

        super().__init__()

        self.window = window
        self.drag_position = None

        self.setCursor(
            QCursor(
                Qt.CursorShape.SizeAllCursor
            )
        )

    def mousePressEvent(
        self,
        event
    ):

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):

            self.drag_position = (
                event.globalPosition().toPoint()
                - self.window.frameGeometry().topLeft()
            )

            event.accept()

            return

        super().mousePressEvent(
            event
        )

    def mouseMoveEvent(
        self,
        event
    ):

        if (
            self.drag_position is not None
            and event.buttons()
            & Qt.MouseButton.LeftButton
        ):

            self.window.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

            event.accept()

            return

        super().mouseMoveEvent(
            event
        )

    def mouseReleaseEvent(
        self,
        event
    ):

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):

            self.drag_position = None

            event.accept()

            return

        super().mouseReleaseEvent(
            event
        )


# ============================================================
# Message
# ============================================================

class SummonMessage(QFrame):

    def __init__(
        self,
        text,
        sender="drax"
    ):

        super().__init__()

        outer = QHBoxLayout(
            self
        )

        outer.setContentsMargins(
            0,
            7,
            0,
            7
        )

        outer.setSpacing(0)

        # ----------------------------------------------------
        # Content
        # ----------------------------------------------------

        content = QFrame()

        content.setMaximumWidth(
            350
        )

        layout = QVBoxLayout(
            content
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(
            3
        )

        self.sender_label = QLabel()
        self.message_label = QLabel()

        self.message_label.setWordWrap(
            True
        )

        self.message_label.setTextFormat(
            Qt.TextFormat.PlainText
        )

        self.message_label.setText(
            text
        )

        # ----------------------------------------------------
        # Drax
        # ----------------------------------------------------

        if sender == "drax":

            self.sender_label.setText(
                "DRAX"
            )

            self.sender_label.setStyleSheet(
                f"""
                color:{theme.SUCCESS};
                font-size:10px;
                font-weight:700;
                letter-spacing:1px;
                """
            )

            self.message_label.setStyleSheet(
                f"""
                color:{theme.TEXT};
                font-size:14px;
                padding-top:2px;
                """
            )

            layout.addWidget(
                self.sender_label
            )

            layout.addWidget(
                self.message_label
            )

            outer.addWidget(
                content,
                0,
                Qt.AlignmentFlag.AlignLeft
            )

            outer.addStretch()

        # ----------------------------------------------------
        # User
        # ----------------------------------------------------

        else:

            self.sender_label.setText(
                "YOU"
            )

            self.sender_label.setAlignment(
                Qt.AlignmentFlag.AlignRight
            )

            self.sender_label.setStyleSheet(
                f"""
                color:{theme.ACCENT};
                font-size:10px;
                font-weight:700;
                letter-spacing:1px;
                """
            )

            self.message_label.setAlignment(
                Qt.AlignmentFlag.AlignRight
            )

            self.message_label.setStyleSheet(
                f"""
                color:{theme.TEXT};
                font-size:14px;
                padding-top:2px;
                """
            )

            layout.addWidget(
                self.sender_label
            )

            layout.addWidget(
                self.message_label
            )

            outer.addStretch()

            outer.addWidget(
                content,
                0,
                Qt.AlignmentFlag.AlignRight
            )


# ============================================================
# Summon Window
# ============================================================

class SummonWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.thread = None
        self.worker = None

        self.animating = False

        self.build_window()
        self.build_ui()

        self.hide()


    # ========================================================
    # Window
    # ========================================================

    def build_window(self):

        self.setWindowTitle(
            "Drax Summon"
        )

        self.resize(
            460,
            620
        )

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            |
            Qt.WindowType.WindowStaysOnTopHint
            |
            Qt.WindowType.Tool
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )


    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        root = QFrame()

        root.setObjectName(
            "summonRoot"
        )

        root.setStyleSheet(
            f"""
            QFrame#summonRoot {{
                background:{theme.WINDOW_BACKGROUND};
                border:1px solid {theme.STATUS_BORDER};
                border-radius:24px;
            }}

            QScrollArea {{
                border:none;
                background:transparent;
            }}

            QScrollBar:vertical {{
                width:6px;
                background:transparent;
            }}

            QScrollBar::handle:vertical {{
                background:#3A3E47;
                border-radius:3px;
                min-height:30px;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height:0px;
            }}
            """
        )

        root_layout = QVBoxLayout(
            root
        )

        root_layout.setContentsMargins(
            20,
            18,
            20,
            16
        )

        root_layout.setSpacing(
            0
        )


        # ====================================================
        # Header
        # ====================================================

        self.header = DragHeader(
            self
        )

        header = QHBoxLayout(
            self.header
        )

        header.setContentsMargins(
            0,
            0,
            0,
            0
        )

        header.setSpacing(
            10
        )


        icon = QLabel(
            theme.DRAX_ICON
        )

        icon.setStyleSheet(
            """
            font-size:27px;
            """
        )

        icon.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )


        titles = QVBoxLayout()

        titles.setSpacing(
            0
        )


        title = QLabel(
            "Drax"
        )

        title.setStyleSheet(
            f"""
            color:{theme.TEXT};
            font-size:18px;
            font-weight:700;
            """
        )

        title.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )


        subtitle = QLabel(
            "Desktop companion"
        )

        subtitle.setStyleSheet(
            f"""
            color:{theme.TEXT_MUTED};
            font-size:10px;
            """
        )

        subtitle.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )


        titles.addWidget(
            title
        )

        titles.addWidget(
            subtitle
        )


        header.addWidget(
            icon
        )

        header.addLayout(
            titles
        )

        header.addStretch()


        online = QLabel(
            "● ONLINE"
        )

        online.setStyleSheet(
            f"""
            color:{theme.SUCCESS};
            font-size:9px;
            font-weight:700;
            letter-spacing:1px;
            """
        )

        online.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        header.addWidget(
            online
        )


        # ----------------------------------------------------
        # Close button
        # ----------------------------------------------------

        close_button = QPushButton(
            "×"
        )

        close_button.setFixedSize(
            28,
            28
        )

        # IMPORTANT:
        # Do NOT give this button the Move cursor.
        close_button.setCursor(
            QCursor(
                Qt.CursorShape.PointingHandCursor
            )
        )

        close_button.setStyleSheet(
            f"""
            QPushButton {{
                background:transparent;
                color:{theme.TEXT_MUTED};
                border:none;
                font-size:20px;
                border-radius:14px;
            }}

            QPushButton:hover {{
                background:#2A2D34;
                color:{theme.TEXT};
            }}
            """
        )

        close_button.clicked.connect(
            self.hide_summon
        )

        header.addWidget(
            close_button
        )


        root_layout.addWidget(
            self.header
        )


        # ====================================================
        # Divider
        # ====================================================

        divider = QFrame()

        divider.setFrameShape(
            QFrame.Shape.HLine
        )

        divider.setStyleSheet(
            f"""
            color:{theme.STATUS_BORDER};
            margin-top:14px;
            margin-bottom:6px;
            """
        )

        root_layout.addWidget(
            divider
        )


        # ====================================================
        # Conversation
        # ====================================================

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )


        self.conversation = QWidget()

        self.messages = QVBoxLayout(
            self.conversation
        )

        self.messages.setContentsMargins(
            4,
            10,
            4,
            10
        )

        self.messages.setSpacing(
            0
        )

        self.messages.addStretch()


        self.scroll.setWidget(
            self.conversation
        )

        root_layout.addWidget(
            self.scroll,
            1
        )


        # ====================================================
        # Empty State
        # ====================================================

        self.empty_state = QFrame()

        empty_layout = QVBoxLayout(
            self.empty_state
        )

        empty_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        empty_layout.setContentsMargins(
            10,
            40,
            10,
            40
        )

        empty_layout.setSpacing(
            8
        )


        empty_icon = QLabel(
            theme.DRAX_ICON
        )

        empty_icon.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        empty_icon.setStyleSheet(
            """
            font-size:42px;
            """
        )


        empty_title = QLabel(
            "What can I do for you?"
        )

        empty_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        empty_title.setStyleSheet(
            f"""
            color:{theme.TEXT};
            font-size:22px;
            font-weight:700;
            """
        )


        empty_subtitle = QLabel(
            "Ask me to control your desktop,"
            "\nlaunch apps, manage tasks, or just talk."
        )

        empty_subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        empty_subtitle.setStyleSheet(
            f"""
            color:{theme.TEXT_SECONDARY};
            font-size:13px;
            """
        )


        examples = QLabel(
            "Try things like\n\n"
            "• Open Chrome\n"
            "• Close Spotify\n"
            "• Set a timer\n"
            "• What's running right now?"
        )

        examples.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        examples.setStyleSheet(
            f"""
            color:{theme.TEXT_MUTED};
            font-size:11px;
            """
        )


        empty_layout.addWidget(
            empty_icon
        )

        empty_layout.addSpacing(
            10
        )

        empty_layout.addWidget(
            empty_title
        )

        empty_layout.addWidget(
            empty_subtitle
        )

        empty_layout.addSpacing(
            10
        )

        empty_layout.addWidget(
            examples
        )


        self.messages.insertWidget(
            0,
            self.empty_state
        )


        # ====================================================
        # Input
        # ====================================================

        input_container = QFrame()

        input_container.setStyleSheet(
            f"""
            QFrame {{
                background:{theme.INPUT_BACKGROUND};
                border:1px solid {theme.INPUT_BORDER};
                border-radius:17px;
            }}
            """
        )

        input_layout = QHBoxLayout(
            input_container
        )

        input_layout.setContentsMargins(
            14,
            5,
            6,
            5
        )

        input_layout.setSpacing(
            6
        )


        self.input = QLineEdit()

        self.input.setPlaceholderText(
            "Ask Drax..."
        )

        self.input.setStyleSheet(
            f"""
            QLineEdit {{
                background:transparent;
                border:none;
                color:{theme.INPUT_TEXT};
                font-size:13px;
                padding:8px 2px;
            }}
            """
        )

        self.input.returnPressed.connect(
            self.send_message
        )

        input_layout.addWidget(
            self.input,
            1
        )


        send = QPushButton(
            "↑"
        )

        send.setFixedSize(
            32,
            32
        )

        send.setCursor(
            QCursor(
                Qt.CursorShape.PointingHandCursor
            )
        )

        send.setStyleSheet(
            f"""
            QPushButton {{
                background:{theme.ACCENT};
                color:white;
                border:none;
                border-radius:16px;
                font-size:17px;
                font-weight:bold;
            }}

            QPushButton:hover {{
                background:{theme.ACCENT_HOVER};
            }}
            """
        )

        send.clicked.connect(
            self.send_message
        )

        input_layout.addWidget(
            send
        )


        root_layout.addWidget(
            input_container
        )


        # ====================================================
        # Hint
        # ====================================================

        hint = QLabel(
            "Ctrl + Space  •  Esc to hide"
        )

        hint.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        hint.setStyleSheet(
            f"""
            color:{theme.TEXT_MUTED};
            font-size:9px;
            padding-top:8px;
            """
        )

        root_layout.addWidget(
            hint
        )


        # ====================================================
        # Main Layout
        # ====================================================

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.addWidget(
            root
        )


    # ========================================================
    # Empty State
    # ========================================================

    def hide_empty_state(self):

        if not hasattr(
            self,
            "empty_state"
        ):

            return

        if not self.empty_state.isVisible():

            return


        effect = QGraphicsOpacityEffect(
            self.empty_state
        )

        self.empty_state.setGraphicsEffect(
            effect
        )


        animation = QPropertyAnimation(
            effect,
            b"opacity",
            self
        )

        animation.setDuration(
            220
        )

        animation.setStartValue(
            1.0
        )

        animation.setEndValue(
            0.0
        )

        animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )


        def remove():

            self.empty_state.hide()

            self.empty_state.setGraphicsEffect(
                None
            )

            animation.deleteLater()


        animation.finished.connect(
            remove
        )

        self.empty_animation = animation

        animation.start()


    # ========================================================
    # Show
    # ========================================================

    def show_summon(self):

        if self.animating:

            return


        if self.isVisible():

            self.hide_summon()

            return


        self.position_window()


        final_rect = self.geometry()


        # Small + slightly shifted starting rectangle.
        start_width = int(
            final_rect.width() * 0.94
        )

        start_height = int(
            final_rect.height() * 0.94
        )

        start_x = (
            final_rect.x()
            + 30
        )

        start_y = (
            final_rect.y()
            + 18
        )

        start_rect = QRect(
            start_x,
            start_y,
            start_width,
            start_height
        )


        self.setGeometry(
            start_rect
        )

        self.setWindowOpacity(
            0.0
        )

        self.show()

        self.raise_()

        self.activateWindow()


        # ----------------------------------------------------
        # Fade
        # ----------------------------------------------------

        fade = QPropertyAnimation(
            self,
            b"windowOpacity"
        )

        fade.setDuration(
            180
        )

        fade.setStartValue(
            0.0
        )

        fade.setEndValue(
            1.0
        )

        fade.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )


        # ----------------------------------------------------
        # Zoom + Slide
        #
        # Geometry animation combines both:
        # small -> full size
        # shifted -> final position
        # ----------------------------------------------------

        geometry = QPropertyAnimation(
            self,
            b"geometry"
        )

        geometry.setDuration(
            230
        )

        geometry.setStartValue(
            start_rect
        )

        geometry.setEndValue(
            final_rect
        )

        geometry.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )


        group = QParallelAnimationGroup(
            self
        )

        group.addAnimation(
            fade
        )

        group.addAnimation(
            geometry
        )


        def finished():

            self.animating = False

            self.setGeometry(
                final_rect
            )

            self.setWindowOpacity(
                1.0
            )

            self.input.setFocus()

            group.deleteLater()


        group.finished.connect(
            finished
        )


        self.animating = True

        self.show_animation = group

        group.start()


    # ========================================================
    # Position
    # ========================================================

    def position_window(self):

        screen = QApplication.primaryScreen()

        geometry = (
            screen.availableGeometry()
        )

        width = 460
        height = 620

        x = (
            geometry.right()
            - width
            - 28
        )

        y = (
            geometry.top()
            + 70
        )

        self.setGeometry(
            x,
            y,
            width,
            height
        )


    # ========================================================
    # Hide
    # ========================================================

    def hide_summon(self):

        if not self.isVisible():

            return

        if self.animating:

            return


        final_rect = self.geometry()


        # Zoom out + slide slightly right/down.
        end_width = int(
            final_rect.width() * 0.94
        )

        end_height = int(
            final_rect.height() * 0.94
        )

        end_rect = QRect(
            final_rect.x() + 30,
            final_rect.y() + 18,
            end_width,
            end_height
        )


        # ----------------------------------------------------
        # Fade out
        # ----------------------------------------------------

        fade = QPropertyAnimation(
            self,
            b"windowOpacity"
        )

        fade.setDuration(
            170
        )

        fade.setStartValue(
            1.0
        )

        fade.setEndValue(
            0.0
        )

        fade.setEasingCurve(
            QEasingCurve.Type.InCubic
        )


        # ----------------------------------------------------
        # Zoom out + slide
        # ----------------------------------------------------

        geometry = QPropertyAnimation(
            self,
            b"geometry"
        )

        geometry.setDuration(
            200
        )

        geometry.setStartValue(
            final_rect
        )

        geometry.setEndValue(
            end_rect
        )

        geometry.setEasingCurve(
            QEasingCurve.Type.InCubic
        )


        group = QParallelAnimationGroup(
            self
        )

        group.addAnimation(
            fade
        )

        group.addAnimation(
            geometry
        )


        def finished():

            self.animating = False

            self.hide()

            self.input.clear()

            self.setWindowOpacity(
                1.0
            )

            group.deleteLater()


        group.finished.connect(
            finished
        )


        self.animating = True

        self.hide_animation = group

        group.start()


    # ========================================================
    # Escape
    # ========================================================

    def keyPressEvent(
        self,
        event
    ):

        if event.key() == (
            Qt.Key.Key_Escape
        ):

            self.hide_summon()

            return


        super().keyPressEvent(
            event
        )


    # ========================================================
    # Add Message
    # ========================================================

    def add_message(
        self,
        text,
        sender="drax",
        hide_empty=True
    ):

        if hide_empty:
            self.hide_empty_state()


        message = SummonMessage(
            text,
            sender
        )


        self.messages.insertWidget(
            self.messages.count() - 1,
            message
        )


        QTimer.singleShot(
            0,
            self.scroll_bottom
        )


    # ========================================================
    # Scroll
    # ========================================================

    def scroll_bottom(self):

        scrollbar = (
            self.scroll.verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )


    # ========================================================
    # Send
    # ========================================================

    def send_message(self):

        command = (
            self.input.text()
            .strip()
        )


        if not command:

            return


        self.input.clear()


        self.add_message(
            command,
            "user"
        )


        self.add_message(
            "Thinking...",
            "drax",
            hide_empty=False
        )


        self.start_worker(
            command
        )


    # ========================================================
    # Worker
    # ========================================================

    def start_worker(
        self,
        command
    ):

        # Don't allow overlapping commands.
        if self.thread is not None:

            return


        self.thread = QThread()

        self.worker = SummonWorker(
            command
        )

        self.worker.moveToThread(
            self.thread
        )


        self.thread.started.connect(
            self.worker.run
        )


        self.worker.response_ready.connect(
            self.receive_response
        )


        self.worker.finished.connect(
            self.thread.quit
        )


        self.worker.finished.connect(
            self.worker.deleteLater
        )


        self.thread.finished.connect(
            self.thread.deleteLater
        )


        self.thread.finished.connect(
            self.worker_finished
        )


        self.thread.start()


    def worker_finished(self):

        self.thread = None
        self.worker = None


    # ========================================================
    # Response
    # ========================================================

    def receive_response(
        self,
        response
    ):

        # Remove the most recent Thinking message.
        for index in range(
            self.messages.count() - 2,
            -1,
            -1
        ):

            item = self.messages.itemAt(
                index
            )

            widget = item.widget()


            if (
                widget
                and isinstance(
                    widget,
                    SummonMessage
                )
                and widget.message_label.text()
                == "Thinking..."
            ):

                widget.deleteLater()

                break


        self.add_message(
            response,
            "drax"
        )