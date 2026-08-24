import sys

from skills.skill_loader import load_skills

from terminal import set_output_callback

from brain import services
from brain import bus, observer

from brain.event_bus import bus

from brain.context import context
from brain.activity import activity
from brain.activity_engine import activity_engine
from PySide6.QtCore import (
    QTimer,
    QObject,
    QThread,
    Signal,
    QEvent,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
)

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsOpacityEffect,
)

from widgets.chat_area import ChatArea
from widgets.status_bar import StatusBar
from widgets.input_bar import InputBar
from widgets.activity_card import ActivityCard

import widgets.theme as theme

from brain.drax import drax

from widgets.summon_window import (
    SummonWindow,
    GlobalHotkeyFilter,
)


class Worker(QObject):

    finished = Signal()

    response_ready = Signal(str)

    def __init__(
        self,
        command
    ):

        super().__init__()

        self.command = command

    def run(self):

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

        self.finished.emit()


class DraxWindow(QWidget):

    output_signal = Signal(object)

    exit_signal = Signal()

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "🤖 DraxAgent"
        )

        self.resize(
            900,
            650
        )

        self.build_ui()

        # ---------------------------------
        # Presence monitor
        # ---------------------------------

        self._presence_state = None

        self.presence_monitor = QTimer(self)
        self.presence_monitor.setInterval(250)
        self.presence_monitor.timeout.connect(
            self.update_presence
        )
        self.presence_monitor.start()

        # ---------------------------------
        # Summon Window
        # ---------------------------------

        self.summon = SummonWindow()

        self.hotkey_filter = (
            GlobalHotkeyFilter(
                self.summon.show_summon
            )
        )

        QApplication.instance().installNativeEventFilter(
            self.hotkey_filter
        )

        # ---------------------------------
        # Observer
        # ---------------------------------

        observer.start()

        # ---------------------------------
        # Signals
        # ---------------------------------

        self.connect_signals()

        bus.subscribe(
            "ai_response",
            self.on_ai_response
        )

        bus.subscribe(
            "activity_updated",
            self.on_activity_changed
        )
        
        QTimer.singleShot(
            0,
            self.update_presence
        )

    # =================================
    # UI
    # =================================

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            theme.WINDOW_PADDING,
            theme.WINDOW_PADDING,
            theme.WINDOW_PADDING,
            theme.WINDOW_PADDING,
        )

        layout.setSpacing(
            theme.SECTION_SPACING
        )

        # ---------------------------------
        # Header
        # ---------------------------------

        header = QWidget()

        header_layout = QHBoxLayout(
            header
        )

        header_layout.setContentsMargins(
            0,
            0,
            0,
            10
        )

        header_layout.setSpacing(
            14
        )

        icon = QLabel(
            "🤖"
        )

        icon.setStyleSheet("""
            font-size:40px;
        """)

        titles = QVBoxLayout()

        self.title = QLabel(
            "DraxAgent"
        )

        self.subtitle = QLabel(
            "Your Personal Desktop Companion"
        )

        self.title.setStyleSheet(
            f"""
            font-size:{theme.TITLE_SIZE}px;
            font-weight:700;
            color:{theme.TEXT};
            """
        )

        self.subtitle.setStyleSheet(
            f"""
            font-size:{theme.SUBTITLE_SIZE}px;
            color:{theme.TEXT_SECONDARY};
            """
        )

        titles.addWidget(
            self.title
        )

        titles.addWidget(
            self.subtitle
        )

        header_layout.addWidget(
            icon
        )

        header_layout.addLayout(
            titles
        )

        header_layout.addStretch()

        # ---------------------------------
        # Presence
        # ---------------------------------

        presence = QHBoxLayout()

        presence.setSpacing(5)

        self.online_dot = QLabel(
            "●"
        )

        self.online_text = QLabel(
            "Online"
        )

        self.online_dot.setStyleSheet(
            """
            color:#49D17D;
            font-size:11px;
            """
        )

        self.online_text.setStyleSheet(
            """
            color:#49D17D;
            font-size:13px;
            font-weight:600;
            """
        )

        presence.addWidget(
            self.online_dot
        )

        presence.addWidget(
            self.online_text
        )

        header_layout.addLayout(
            presence
        )

        # ---------------------------------
        # Presence animation
        # ---------------------------------

        # Separate opacity effects for the dot and text.
        # This lets the whole presence indicator fade,
        # instead of only the dot.
        
        self.presence_dot_effect = (
            QGraphicsOpacityEffect(
                self.online_dot
            )
        )

        self.presence_text_effect = (
            QGraphicsOpacityEffect(
                self.online_text
            )
        )

        self.online_dot.setGraphicsEffect(
            self.presence_dot_effect
        )

        self.online_text.setGraphicsEffect(
            self.presence_text_effect
        )

        self.presence_dot_effect.setOpacity(
            1.0
        )

        self.presence_text_effect.setOpacity(
            1.0
        )

        # Current transition animation.
        self.presence_transition = None

        # Continuous breathing animation for the
        # Online dot.
        self.presence_pulse = (
            QPropertyAnimation(
                self.presence_dot_effect,
                b"opacity",
                self
            )
        )

        self.presence_pulse.setDuration(
            1200
        )

        self.presence_pulse.setStartValue(
            1.0
        )

        self.presence_pulse.setEndValue(
            0.35
        )

        self.presence_pulse.setEasingCurve(
            QEasingCurve.InOutSine
        )

        self.presence_pulse.setLoopCount(
            -1
        )

        self.presence_pulse.start()

        # ---------------------------------
        # Activity Card
        # ---------------------------------

        self.activity_card = (
            ActivityCard()
        )

        # ---------------------------------
        # Existing UI
        # ---------------------------------

        self.status_bar = StatusBar()

        self.chat = ChatArea()

        self.input = InputBar()

        # ---------------------------------
        # Main layout
        # ---------------------------------

        layout.addWidget(
            header
        )

        layout.addWidget(
            self.activity_card
        )

        layout.addWidget(
            self.status_bar
        )

        layout.addWidget(
            self.chat,
            1
        )

        layout.addWidget(
            self.input
        )

        self.setStyleSheet(
            f"""
            QWidget {{
                background:{theme.WINDOW_BACKGROUND};
                color:{theme.TEXT};
            }}
            """
        )

    # =================================
    # SIGNALS
    # =================================

    def connect_signals(self):

        self.input.send_clicked.connect(
            self.process_command
        )

        self.output_signal.connect(
            self.handle_output
        )

        self.exit_signal.connect(
            self.schedule_exit
        )

        set_output_callback(
            lambda text, kind:
            self.output_signal.emit(
                (text, kind)
            )
        )

        bus.subscribe(
            "exit_requested",
            lambda:
            self.exit_signal.emit()
        )
        
    # =================================
    # PRESENCE
    # =================================

    def update_presence(self):

        is_foreground = (
            QApplication.activeWindow() is self
            or self.isActiveWindow()
        )

        # ---------------------------------
        # DraxAgent is foreground
        # ---------------------------------

        if is_foreground:

            # Already online.
            if self._presence_state == "online":
                return

            # Already waiting for the delayed
            # Away -> Online transition.
            if (
                self._presence_state
                == "transitioning"
            ):
                return

            if not hasattr(
                self,
                "presence_delay"
            ):

                self.presence_delay = (
                    QTimer(self)
                )

                self.presence_delay.setSingleShot(
                    True
                )

                self.presence_delay.timeout.connect(
                    self.show_online_presence
                )

            self._presence_state = (
                "transitioning"
            )

            # Keep Away visible for a moment
            # before starting the fade.
            self.presence_delay.start(
                700
            )

            return

        # ---------------------------------
        # DraxAgent is background
        # ---------------------------------

        if hasattr(
            self,
            "presence_delay"
        ):

            self.presence_delay.stop()

        if self._presence_state != "away":

            self.show_away_presence()


    # ---------------------------------
    # Shared fade transition
    # ---------------------------------

    def _fade_presence_to(
        self,
        state
    ):

        # Stop any previous transition.
        if self.presence_transition:

            self.presence_transition.stop()

        # Stop the breathing pulse while
        # transitioning.
        self.presence_pulse.stop()

        # Fade both dot and text out.
        fade_out = (
            QParallelAnimationGroup(
                self
            )
        )

        dot_out = QPropertyAnimation(
            self.presence_dot_effect,
            b"opacity",
            self
        )

        text_out = QPropertyAnimation(
            self.presence_text_effect,
            b"opacity",
            self
        )

        for animation in (
            dot_out,
            text_out
        ):

            animation.setDuration(
                220
            )

            animation.setEasingCurve(
                QEasingCurve.InOutSine
            )

        dot_out.setStartValue(
            self.presence_dot_effect.opacity()
        )

        dot_out.setEndValue(
            0.0
        )

        text_out.setStartValue(
            self.presence_text_effect.opacity()
        )

        text_out.setEndValue(
            0.0
        )

        fade_out.addAnimation(
            dot_out
        )

        fade_out.addAnimation(
            text_out
        )

        self.presence_transition = (
            fade_out
        )

        def apply_new_state():

            if state == "online":

                self._presence_state = (
                    "online"
                )

                self.online_text.setText(
                    "Online"
                )

                self.online_dot.setStyleSheet(
                    """
                    color:#49D17D;
                    font-size:11px;
                    """
                )

                self.online_text.setStyleSheet(
                    """
                    color:#49D17D;
                    font-size:13px;
                    font-weight:600;
                    """
                )

            else:

                self._presence_state = (
                    "away"
                )

                self.online_text.setText(
                    "Away"
                )

                self.online_dot.setStyleSheet(
                    """
                    color:#6B7280;
                    font-size:11px;
                    """
                )

                self.online_text.setStyleSheet(
                    """
                    color:#8B93A1;
                    font-size:13px;
                    font-weight:600;
                    """
                )

            # Fade both back in.
            fade_in = (
                QParallelAnimationGroup(
                    self
                )
            )

            dot_in = QPropertyAnimation(
                self.presence_dot_effect,
                b"opacity",
                self
            )

            text_in = QPropertyAnimation(
                self.presence_text_effect,
                b"opacity",
                self
            )

            for animation in (
                dot_in,
                text_in
            ):

                animation.setDuration(
                    320
                )

                animation.setEasingCurve(
                    QEasingCurve.InOutSine
                )

            dot_in.setStartValue(
                0.0
            )

            dot_in.setEndValue(
                1.0
            )

            text_in.setStartValue(
                0.0
            )

            text_in.setEndValue(
                1.0
            )

            fade_in.addAnimation(
                dot_in
            )

            fade_in.addAnimation(
                text_in
            )

            self.presence_transition = (
                fade_in
            )

            def transition_finished():

                # Only Online gets the breathing pulse.
                if (
                    self._presence_state
                    == "online"
                ):

                    self.presence_pulse.start()

            fade_in.finished.connect(
                transition_finished
            )

            fade_in.start()

        fade_out.finished.connect(
            apply_new_state
        )

        fade_out.start()


    # ---------------------------------
    # Away
    # ---------------------------------

    def show_away_presence(self):

        # Don't interrupt an existing Away state.
        if self._presence_state == "away":
            return

        self._fade_presence_to(
            "away"
        )


    # ---------------------------------
    # Online
    # ---------------------------------

    def show_online_presence(self):

        # Make sure Drax is STILL foreground.
        is_foreground = (
            QApplication.activeWindow() is self
            or self.isActiveWindow()
        )

        if not is_foreground:

            self._presence_state = (
                "transitioning"
            )

            self.show_away_presence()

            return

        self._fade_presence_to(
            "online"
        )


    # ---------------------------------
    # Window activation
    # ---------------------------------

    def changeEvent(
        self,
        event
    ):

        if event.type() in (
            QEvent.WindowActivate,
            QEvent.WindowDeactivate
        ):

            self.update_presence()

        super().changeEvent(
            event
        )
    # =================================
    # ACTIVITY
    # =================================

    def on_activity_changed(
        self,
        data=None
    ):

        # ActivityEngine has finished updating
        # the shared Activity state. Read the
        # current context now so the card never
        # renders one activity behind.

        application = (
            context.current_application
            or activity.application
            or "Unknown"
        )

        process = (
            context.current_process
        )

        # ---------------------------------
        # Ignore DraxAgent itself
        # ---------------------------------

        if activity_engine.is_drax_window(
            application,
            process
        ):

            return

        # ---------------------------------
        # Render the latest activity state
        # ---------------------------------

        self.activity_card.update_activity(
            activity.name,
            application,
            context.current_window,
            activity.started_at
        )

    # =================================
    # COMMAND
    # =================================

    def process_command(
        self,
        command
    ):

        command = command.strip()

        if not command:
            return

        self.chat.add_user_message(
            command
        )

        self.chat.show_typing()

        self.thread = QThread()

        self.worker = Worker(
            command
        )

        self.worker.moveToThread(
            self.thread
        )

        self.worker.response_ready.connect(
            self.chat.add_drax_message
        )

        self.thread.started.connect(
            self.worker.run
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
            self.chat.hide_typing
        )

        self.thread.start()

        bus.emit(
            "message",
            command
        )

    # =================================
    # OUTPUT
    # =================================

    def handle_output(
        self,
        data
    ):

        text, kind = data

        # ---------------------------------
        # Temporary status
        # ---------------------------------

        if kind == "status":

            is_closing = (
                "closing"
                in text.lower()
                or text.startswith("🛑")
            )

            self.status_bar.show_message(
                text,
                color=(
                    "#FF4D5A"
                    if is_closing
                    else "#49D17D"
                )
            )

            return

        # ---------------------------------
        # Finished status
        # ---------------------------------

        if kind == "status_done":

            is_closing = (
                "closed"
                in text.lower()
                or "closing"
                in text.lower()
            )

            self.status_bar.show_message(
                text,
                color=(
                    "#FF4D5A"
                    if is_closing
                    else "#49D17D"
                )
            )

            self.status_bar.finish_message(
                delay=(
                    800
                    if is_closing
                    else 300
                )
            )

            return

        # ---------------------------------
        # Assistant
        # ---------------------------------

        if kind == "assistant":

            self.chat.add_drax_message(
                text
            )

            return

        # ---------------------------------
        # Success
        # ---------------------------------

        if kind == "success":

            self.chat.add_drax_message(
                "✅ " + text
            )

            self.status_bar.finish_message(
                delay=1200
            )

            return

        # ---------------------------------
        # Error
        # ---------------------------------

        if kind == "error":

            self.chat.add_drax_message(
                "❌ " + text
            )

            self.status_bar.finish_message(
                delay=1200
            )

            return

        # ---------------------------------
        # Other output
        # ---------------------------------

        self.chat.add_drax_message(
            text
        )

    # =================================
    # AI RESPONSE
    # =================================

    def on_ai_response(
        self,
        message
    ):

        self.chat.show_typing()

        QTimer.singleShot(
            2500,
            lambda:
            self.finish_ai_response(
                message
            )
        )

    def finish_ai_response(
        self,
        message
    ):

        self.chat.hide_typing()

        self.chat.add_drax_message(
            message
        )

    # =================================
    # EXIT
    # =================================

    def schedule_exit(self):

        QTimer.singleShot(
            3500,
            QApplication.quit
        )

    # =================================
    # CLOSE
    # =================================

    def closeEvent(
        self,
        event
    ):

        if hasattr(
            self,
            "hotkey_filter"
        ):

            self.hotkey_filter.unregister()

            QApplication.instance().removeNativeEventFilter(
                self.hotkey_filter
            )

        if hasattr(
            self,
            "summon"
        ):

            self.summon.close()

        event.accept()


# =====================================
# MAIN
# =====================================

def main():

    load_skills()

    app = QApplication(
        sys.argv
    )

    window = DraxWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":

    main()