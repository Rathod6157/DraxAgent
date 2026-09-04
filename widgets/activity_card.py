from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QGraphicsOpacityEffect,
)

from PySide6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
)

import widgets.theme as theme


class ActivityCard(QWidget):

    def __init__(self):
        super().__init__()

        self.current_window_started = None
        self.current_context = ""

        self.build_ui()

        # ---------------------------------
        # Duration timer
        # ---------------------------------

        self.duration_timer = QTimer(self)

        self.duration_timer.setInterval(
            1000
        )

        self.duration_timer.timeout.connect(
            self.update_duration
        )

        # ---------------------------------
        # Activity transition
        #
        # Only the content fades.
        # The card itself never moves.
        # ---------------------------------

        self.content_opacity = (
            QGraphicsOpacityEffect(
                self.content_container
            )
        )

        self.content_container.setGraphicsEffect(
            self.content_opacity
        )

        self.content_fade = QPropertyAnimation(
            self.content_opacity,
            b"opacity",
            self
        )

        self.content_fade.setDuration(
            180
        )

        self.content_fade.setEasingCurve(
            QEasingCurve.OutCubic
        )

        # ---------------------------------
        # Live indicator pulse
        # ---------------------------------

        self.indicator_opacity = (
            QGraphicsOpacityEffect(
                self.indicator
            )
        )

        self.indicator.setGraphicsEffect(
            self.indicator_opacity
        )

        self.indicator_pulse = QPropertyAnimation(
            self.indicator_opacity,
            b"opacity",
            self
        )

        self.indicator_pulse.setDuration(
            1400
        )

        self.indicator_pulse.setStartValue(
            1.0
        )

        self.indicator_pulse.setKeyValueAt(
            0.5,
            0.42
        )

        self.indicator_pulse.setEndValue(
            1.0
        )

        self.indicator_pulse.setEasingCurve(
            QEasingCurve.InOutSine
        )

        self.indicator_pulse.setLoopCount(
            -1
        )

        self.indicator_pulse.start()

    # =================================
    # UI
    # =================================

    def build_ui(self):

        outer_layout = QHBoxLayout(
            self
        )

        outer_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        outer_layout.setSpacing(
            0
        )

        # ---------------------------------
        # Accent rail
        # ---------------------------------

        self.accent_rail = QFrame()

        self.accent_rail.setFixedWidth(
            3
        )

        self.accent_rail.setStyleSheet(f"""
            background: {theme.ACCENT};
            border: none;
            border-radius: 2px;
        """)

        outer_layout.addWidget(
            self.accent_rail
        )

        # ---------------------------------
        # Main card
        # ---------------------------------

        self.card = QFrame()

        self.card.setObjectName(
            "activityCard"
        )

        self.card.setStyleSheet(f"""
            QFrame#activityCard {{
                background: {theme.STATUS_BUBBLE};
                border: 1px solid {theme.STATUS_BORDER};
                border-left: none;
                border-radius: 0px 12px 12px 0px;
            }}
        """)

        outer_layout.addWidget(
            self.card
        )

        # ---------------------------------
        # Card layout
        # ---------------------------------

        layout = QVBoxLayout(
            self.card
        )

        layout.setContentsMargins(
            15,
            11,
            15,
            12
        )

        layout.setSpacing(
            5
        )

        # ---------------------------------
        # Header
        # ---------------------------------

        header = QHBoxLayout()

        header.setContentsMargins(
            0,
            0,
            0,
            0
        )

        header.setSpacing(
            6
        )

        # Live dot

        self.indicator = QLabel(
            "●"
        )

        self.indicator.setFixedWidth(
            8
        )

        self.indicator.setAlignment(
            Qt.AlignCenter
        )

        self.indicator.setStyleSheet(f"""
            color: {theme.SUCCESS};
            font-size: 8px;
            background: transparent;
            border: none;
        """)

        header.addWidget(
            self.indicator
        )

        # Header label

        self.header_label = QLabel(
            "CURRENTLY"
        )

        self.header_label.setStyleSheet(f"""
            color: {theme.TEXT_MUTED};
            font-size: 9px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        header.addWidget(
            self.header_label
        )

        header.addStretch()

        # Live state

        self.live_label = QLabel(
            "LIVE"
        )

        self.live_label.setStyleSheet(f"""
            color: {theme.SUCCESS};
            font-size: 8px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        header.addWidget(
            self.live_label
        )

        layout.addLayout(
            header
        )

        # ---------------------------------
        # Content container
        #
        # This is what fades during an update.
        # The actual card stays stationary.
        # ---------------------------------

        self.content_container = QWidget()

        self.content_container.setStyleSheet("""
            background: transparent;
            border: none;
        """)

        content_layout = QVBoxLayout(
            self.content_container
        )

        content_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        content_layout.setSpacing(
            3
        )

        # ---------------------------------
        # Activity row
        # ---------------------------------

        activity_row = QHBoxLayout()

        activity_row.setContentsMargins(
            0,
            0,
            0,
            0
        )

        activity_row.setSpacing(
            10
        )

        self.activity_label = QLabel(
            "Unknown"
        )

        self.activity_label.setSizePolicy(
            self.activity_label.sizePolicy().horizontalPolicy(),
            self.activity_label.sizePolicy().verticalPolicy()
        )

        self.activity_label.setStyleSheet(f"""
            color: {theme.TEXT};
            font-size: 16px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        activity_row.addWidget(
            self.activity_label
        )

        activity_row.addStretch()

        self.duration_label = QLabel(
            "Just now"
        )

        self.duration_label.setAlignment(
            Qt.AlignRight |
            Qt.AlignVCenter
        )

        self.duration_label.setStyleSheet(f"""
            color: {theme.TEXT_MUTED};
            font-size: 10px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)

        activity_row.addWidget(
            self.duration_label
        )

        content_layout.addLayout(
            activity_row
        )

        # ---------------------------------
        # Application
        # ---------------------------------

        application_row = QHBoxLayout()

        application_row.setContentsMargins(
            0,
            0,
            0,
            0
        )

        application_row.setSpacing(
            6
        )

        self.application_marker = QLabel(
            "▸"
        )

        self.application_marker.setStyleSheet(f"""
            color: {theme.ACCENT};
            font-size: 10px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        application_row.addWidget(
            self.application_marker
        )

        self.application_label = QLabel(
            "Waiting for activity..."
        )

        self.application_label.setStyleSheet(f"""
            color: {theme.TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)

        self.application_label.setWordWrap(
            False
        )

        self.application_label.setTextInteractionFlags(
            Qt.NoTextInteraction
        )

        application_row.addWidget(
            self.application_label
        )

        application_row.addStretch()

        content_layout.addLayout(
            application_row
        )

        # ---------------------------------
        # Drax interpretation
        # ---------------------------------

        self.context_label = QLabel(
            ""
        )

        self.context_label.setStyleSheet(f"""
            color: {theme.TEXT_MUTED};
            font-size: 10px;
            font-weight: 400;
            background: transparent;
            border: none;
        """)

        self.context_label.setWordWrap(
            False
        )

        self.context_label.setTextInteractionFlags(
            Qt.NoTextInteraction
        )

        self.context_label.hide()

        content_layout.addWidget(
            self.context_label
        )

        layout.addWidget(
            self.content_container
        )

        # ---------------------------------
        # Separator
        # ---------------------------------

        self.separator = QFrame()

        self.separator.setFixedHeight(
            1
        )

        self.separator.setStyleSheet(f"""
            background: {theme.STATUS_BORDER};
            border: none;
        """)

        layout.addSpacing(
            2
        )

        layout.addWidget(
            self.separator
        )

        # ---------------------------------
        # Card sizing
        # ---------------------------------

        self.setMinimumHeight(
            104
        )

        self.setSizePolicy(
            self.sizePolicy().horizontalPolicy(),
            self.sizePolicy().verticalPolicy()
        )

    # =================================
    # UPDATE
    # =================================

    def update_activity(
        self,
        activity_name,
        application,
        window_title,
        started_at,
        context=""
    ):

        # ---------------------------------
        # Normalize values
        # ---------------------------------

        activity_name = (
            str(activity_name).strip()
            if activity_name
            else "Unknown"
        )

        display_application = (
            application
            or "Unknown application"
        )

        display_application = str(
            display_application
        ).strip()

        if not display_application:
            display_application = (
                "Unknown application"
            )

        context = (
            str(context).strip()
            if context
            else ""
        )

        # ---------------------------------
        # Stop previous transition
        # ---------------------------------

        if self.content_fade.state():
            self.content_fade.stop()

        # ---------------------------------
        # Fade content out slightly
        # ---------------------------------

        self.content_fade.setStartValue(
            1.0
        )

        self.content_fade.setEndValue(
            0.72
        )

        self.content_fade.start()

        # ---------------------------------
        # Update activity
        # ---------------------------------

        self.activity_label.setText(
            activity_name
        )

        self.application_label.setText(
            display_application
        )

        # ---------------------------------
        # Optional Drax context
        # ---------------------------------

        if context:

            self.context_label.setText(
                context
            )

            self.context_label.show()

        else:

            self.context_label.clear()
            self.context_label.hide()

        # ---------------------------------
        # Duration
        # ---------------------------------

        self.current_window_started = (
            started_at
        )

        self.update_duration()

        self.duration_timer.start()

        # ---------------------------------
        # Fade content back in
        # ---------------------------------

        self.content_fade.stop()

        self.content_fade.setStartValue(
            0.72
        )

        self.content_fade.setEndValue(
            1.0
        )

        self.content_fade.start()

    # =================================
    # DURATION
    # =================================

    def update_duration(self):

        if self.current_window_started is None:
            return

        import time

        elapsed = max(
            0,
            int(
                time.time()
                - self.current_window_started
            )
        )

        # ---------------------------------
        # Just now
        # ---------------------------------

        if elapsed < 60:

            text = "Just now"

        # ---------------------------------
        # Minutes
        # ---------------------------------

        elif elapsed < 3600:

            minutes = elapsed // 60

            text = (
                f"{minutes} minute"
                if minutes == 1
                else f"{minutes} minutes"
            )

            text += " active"

        # ---------------------------------
        # Hours
        # ---------------------------------

        else:

            hours = elapsed // 3600

            minutes = (
                elapsed % 3600
            ) // 60

            if minutes:

                text = (
                    f"{hours}h "
                    f"{minutes}m active"
                )

            else:

                text = (
                    f"{hours}h active"
                )

        self.duration_label.setText(
            text
        )