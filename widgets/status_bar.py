from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QGraphicsOpacityEffect,
)

from PySide6.QtCore import (
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
)

import widgets.theme as theme


class StatusBar(QWidget):

    def __init__(self):
        super().__init__()

        self.status_color = "#49D17D"

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
        QWidget {{
            background: {theme.DRAX_BUBBLE};
            border-radius: 12px;
        }}

        QLabel {{
            color: {theme.TEXT};
            font-size: 13px;
        }}
        """)

        # -----------------------------
        # Status dot
        # -----------------------------

        self.set_dot_color(
            self.status_color
        )

        # -----------------------------
        # Dot animation
        # -----------------------------

        self.dots = 1

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.animate
        )

        # -----------------------------
        # Fade effect
        # -----------------------------

        self.opacity_effect = QGraphicsOpacityEffect(
            self
        )

        self.setGraphicsEffect(
            self.opacity_effect
        )

        self.opacity_effect.setOpacity(
            0.0
        )

        self.fade_animation = QPropertyAnimation(
            self.opacity_effect,
            b"opacity",
            self
        )

        self.fade_animation.setEasingCurve(
            QEasingCurve.Type.InOutCubic
        )

        # -----------------------------
        # Delayed fade-out
        # -----------------------------

        self.fade_timer = QTimer(self)

        self.fade_timer.setSingleShot(True)

        self.fade_timer.timeout.connect(
            self.fade_out
        )

        self.is_fading = False

        self.hide()


    # =================================
    # DOT COLOR
    # =================================

    def set_dot_color(
        self,
        color
    ):

        self.status_color = color

        self.icon.setStyleSheet(
            f"""
            color: {color};
            font-size: 13px;
            """
        )


    # =================================
    # SHOW / START
    # =================================

    def show_message(
        self,
        text,
        color=None
    ):

        self.fade_timer.stop()
        self.fade_animation.stop()

        self.is_fading = False

        self.label.setText(text)

        self.dots = 1
        self.icon.setText("●")

        if color is not None:

            self.set_dot_color(
                color
            )

        else:

            self.set_dot_color(
                "#49D17D"
            )

        self.show()

        self.opacity_effect.setOpacity(
            0.0
        )

        # Fade IN
        self.fade_animation.setDuration(
            300
        )

        self.fade_animation.setStartValue(
            0.0
        )

        self.fade_animation.setEndValue(
            1.0
        )

        self.fade_animation.start()

        # Start dots
        self.timer.start(350)


    # =================================
    # UPDATE MESSAGE
    # =================================

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

        self.label.setText(
            text
        )

        if color is not None:

            self.set_dot_color(
                color
            )


    # =================================
    # FINISH
    # =================================

    def finish_message(
        self,
        text=None,
        delay=1200
    ):

        self.timer.stop()

        if text is not None:

            self.label.setText(
                text
            )

        self.dots = 1
        self.icon.setText("●")

        # Wait before fading out.
        self.fade_timer.start(
            delay
        )


    # =================================
    # FADE OUT
    # =================================

    def fade_out(self):

        if self.is_fading:
            return

        self.is_fading = True

        self.timer.stop()
        self.fade_animation.stop()

        self.fade_animation.setDuration(
            500
        )

        self.fade_animation.setStartValue(
            self.opacity_effect.opacity()
        )

        self.fade_animation.setEndValue(
            0.0
        )

        self.fade_animation.finished.connect(
            self._finish_fade
        )

        self.fade_animation.start()


    def _finish_fade(self):

        try:

            self.fade_animation.finished.disconnect(
                self._finish_fade
            )

        except RuntimeError:

            pass

        self.hide()

        self.label.clear()

        self.opacity_effect.setOpacity(
            0.0
        )

        self.is_fading = False


    # =================================
    # FORCE HIDE
    # =================================

    def hide_message(self):

        self.fade_timer.stop()
        self.timer.stop()
        self.fade_animation.stop()

        self.hide()

        self.opacity_effect.setOpacity(
            0.0
        )

        self.dots = 1
        self.icon.setText("●")

        self.set_dot_color(
            "#49D17D"
        )

        self.is_fading = False


    # =================================
    # DOTS
    # =================================

    def animate(self):

        self.dots += 1

        if self.dots > 3:

            self.dots = 1

        self.icon.setText(
            "●" * self.dots
        )