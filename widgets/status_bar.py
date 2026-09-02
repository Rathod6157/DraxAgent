from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
)

from PySide6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    Property,
)

import widgets.theme as theme


class StatusBar(QWidget):

    def __init__(self):
        super().__init__()

        self._opacity = 1.0
        self._visible_state = False

        self.dots = 1
        self.status_color = theme.SUCCESS

        self._build_ui()
        self._build_timers()
        self._build_animations()

        self.hide()

    # =========================================================
    # UI
    # =========================================================

    def _build_ui(self):

        self.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            14,
            7,
            14,
            7
        )

        layout.setSpacing(8)

        # -----------------------------------------------------
        # Status indicator
        # -----------------------------------------------------

        self.icon = QLabel("●")

        self.icon.setFixedWidth(10)

        self.icon.setAlignment(
            Qt.AlignCenter
        )

        # -----------------------------------------------------
        # Status text
        # -----------------------------------------------------

        self.label = QLabel("")

        self.label.setAlignment(
            Qt.AlignVCenter
        )

        self.label.setTextInteractionFlags(
            Qt.NoTextInteraction
        )

        # -----------------------------------------------------
        # Layout
        # -----------------------------------------------------

        layout.addWidget(
            self.icon
        )

        layout.addWidget(
            self.label
        )

        layout.addStretch()

        # -----------------------------------------------------
        # Styling
        # -----------------------------------------------------

        self.setStyleSheet(f"""
            StatusBar {{
                background: {theme.STATUS_BACKGROUND};
                border: 1px solid {theme.STATUS_BORDER};
                border-radius: 12px;
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        self.label.setStyleSheet(f"""
            color: {theme.TEXT_SECONDARY};
            font-size: {theme.STATUS_SIZE}px;
            font-weight: 500;
        """)

        self.icon.setStyleSheet(f"""
            color: {theme.SUCCESS};
            font-size: 9px;
        """)

        self.setMinimumHeight(34)

    # =========================================================
    # TIMERS
    # =========================================================

    def _build_timers(self):

        # Thinking / processing dots
        self.dots_timer = QTimer(self)

        self.dots_timer.setInterval(380)

        self.dots_timer.timeout.connect(
            self._animate_dots
        )

        # Delayed fade-out
        self.fade_timer = QTimer(self)

        self.fade_timer.setSingleShot(True)

        self.fade_timer.timeout.connect(
            self.fade_out
        )

    # =========================================================
    # ANIMATIONS
    # =========================================================

    def _build_animations(self):

        self.fade_animation = QPropertyAnimation(
            self,
            b"opacity",
            self
        )

        self.fade_animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        self.fade_animation.finished.connect(
            self._fade_finished
        )

    # =========================================================
    # OPACITY PROPERTY
    # =========================================================

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):

        self._opacity = value

        # Qt widgets don't have a native opacity property,
        # so use window opacity only when supported.
        self.setWindowOpacity(
            max(0.0, min(1.0, value))
        )

    opacity = Property(
        float,
        get_opacity,
        set_opacity
    )

    # =========================================================
    # DOT COLOR
    # =========================================================

    def set_dot_color(self, color):

        self.status_color = color

        self.icon.setStyleSheet(f"""
            color: {color};
            font-size: 9px;
        """)

    # =========================================================
    # SHOW MESSAGE
    # =========================================================

    def show_message(
        self,
        text,
        color=None
    ):

        self.fade_timer.stop()
        self.fade_animation.stop()

        self._visible_state = True

        # -----------------------------------------------------
        # Text
        # -----------------------------------------------------

        self.label.setText(
            text
        )

        # -----------------------------------------------------
        # Color
        # -----------------------------------------------------

        self.set_dot_color(
            color if color is not None
            else theme.SUCCESS
        )

        # -----------------------------------------------------
        # Dots
        # -----------------------------------------------------

        self.dots = 1

        self.icon.setText("●")

        self.dots_timer.start()

        # -----------------------------------------------------
        # Show
        # -----------------------------------------------------

        if not self.isVisible():

            self.setWindowOpacity(
                0.0
            )

            self._opacity = 0.0

            self.show()

            self.fade_animation.setDuration(
                180
            )

            self.fade_animation.setStartValue(
                0.0
            )

            self.fade_animation.setEndValue(
                1.0
            )

            self.fade_animation.start()

        else:

            self.setWindowOpacity(
                1.0
            )

            self._opacity = 1.0

    # =========================================================
    # UPDATE MESSAGE
    # =========================================================

    def update_message(
        self,
        text,
        color=None
    ):

        if not self.isVisible():

            self.show_message(
                text,
                color
            )

            return

        self.fade_timer.stop()

        self.label.setText(
            text
        )

        if color is not None:

            self.set_dot_color(
                color
            )

    # =========================================================
    # FINISH MESSAGE
    # =========================================================

    def finish_message(
        self,
        text=None,
        delay=900
    ):

        self.dots_timer.stop()

        self.dots = 1
        self.icon.setText("●")

        if text is not None:

            self.label.setText(
                text
            )

        self.fade_timer.start(
            max(0, delay)
        )

    # =========================================================
    # FADE OUT
    # =========================================================

    def fade_out(self):

        if not self.isVisible():
            return

        self.fade_timer.stop()
        self.dots_timer.stop()

        self.fade_animation.stop()

        self.fade_animation.setDuration(
            220
        )

        self.fade_animation.setStartValue(
            self.windowOpacity()
        )

        self.fade_animation.setEndValue(
            0.0
        )

        self.fade_animation.start()

    # =========================================================
    # FADE COMPLETE
    # =========================================================

    def _fade_finished(self):

        if self.windowOpacity() > 0.01:
            return

        self.hide()

        self.label.clear()

        self.dots = 1

        self.icon.setText(
            "●"
        )

        self._opacity = 0.0

        self._visible_state = False

        self.setWindowOpacity(
            1.0
        )

    # =========================================================
    # FORCE HIDE
    # =========================================================

    def hide_message(self):

        self.fade_timer.stop()
        self.dots_timer.stop()
        self.fade_animation.stop()

        self.hide()

        self.label.clear()

        self.dots = 1

        self.icon.setText(
            "●"
        )

        self.set_dot_color(
            theme.SUCCESS
        )

        self._opacity = 1.0

        self.setWindowOpacity(
            1.0
        )

        self._visible_state = False

    # =========================================================
    # DOT ANIMATION
    # =========================================================

    def _animate_dots(self):

        if not self.isVisible():
            return

        self.dots += 1

        if self.dots > 3:
            self.dots = 1

        self.icon.setText(
            "●" * self.dots
        )