from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
)

from PySide6.QtCore import Qt, QTimer

import widgets.theme as theme


class ActivityCard(QWidget):

    def __init__(self):
        super().__init__()

        self.current_window_started = None

        self.build_ui()

        self.duration_timer = QTimer(self)
        self.duration_timer.timeout.connect(
            self.update_duration
        )

    # =================================
    # UI
    # =================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            14,
            10,
            14,
            10
        )

        layout.setSpacing(4)

        # ---------------------------------
        # Header
        # ---------------------------------

        header = QHBoxLayout()

        header.setSpacing(6)

        self.indicator = QLabel("●")

        self.indicator.setFixedWidth(8)

        self.indicator.setStyleSheet(f"""
            color: {theme.SUCCESS};
            font-size: 9px;
        """)

        self.header_label = QLabel(
            "CURRENTLY"
        )

        self.header_label.setStyleSheet(f"""
            color: {theme.TEXT_MUTED};
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 1px;
        """)

        header.addWidget(
            self.indicator
        )

        header.addWidget(
            self.header_label
        )

        header.addStretch()

        self.live_label = QLabel(
            "LIVE"
        )

        self.live_label.setStyleSheet(f"""
            color: {theme.SUCCESS};
            font-size: 8px;
            font-weight: 700;
            letter-spacing: 1px;
        """)

        header.addWidget(
            self.live_label
        )

        # ---------------------------------
        # Main activity row
        # ---------------------------------

        activity_row = QHBoxLayout()

        activity_row.setSpacing(8)

        self.activity_label = QLabel(
            "Unknown"
        )

        self.activity_label.setStyleSheet(f"""
            color: {theme.TEXT};
            font-size: 16px;
            font-weight: 700;
        """)

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
        """)

        activity_row.addWidget(
            self.activity_label
        )

        activity_row.addStretch()

        activity_row.addWidget(
            self.duration_label
        )

        # ---------------------------------
        # Application
        # ---------------------------------

        self.application_label = QLabel(
            "Waiting for activity..."
        )

        self.application_label.setStyleSheet(f"""
            color: {theme.TEXT_SECONDARY};
            font-size: 11px;
        """)

        self.application_label.setWordWrap(
            False
        )

        self.application_label.setTextInteractionFlags(
            Qt.NoTextInteraction
        )

        # ---------------------------------
        # Separator
        # ---------------------------------

        self.separator = QFrame()

        self.separator.setFrameShape(
            QFrame.HLine
        )

        self.separator.setFixedHeight(
            1
        )

        self.separator.setStyleSheet(f"""
            background: {theme.STATUS_BORDER};
            border: none;
        """)

        # ---------------------------------
        # Layout
        # ---------------------------------

        layout.addLayout(
            header
        )

        layout.addLayout(
            activity_row
        )

        layout.addWidget(
            self.application_label
        )

        layout.addSpacing(
            2
        )

        layout.addWidget(
            self.separator
        )

        # ---------------------------------
        # Card
        # ---------------------------------

        self.setStyleSheet(f"""
            ActivityCard {{
                background: {theme.STATUS_BUBBLE};
                border: 1px solid {theme.STATUS_BORDER};
                border-radius: 12px;
            }}
        """)

        self.setMinimumHeight(
            88
        )

    # =================================
    # UPDATE
    # =================================

    def update_activity(
        self,
        activity_name,
        application,
        window_title,
        started_at
    ):

        self.activity_label.setText(
            activity_name or "Unknown"
        )

        # ---------------------------------
        # Application
        # ---------------------------------

        display_application = (
            application
            or window_title
            or "Unknown application"
        )

        self.application_label.setText(
            display_application
        )

        # ---------------------------------
        # Duration
        # ---------------------------------

        self.current_window_started = (
            started_at
        )

        self.update_duration()

        self.duration_timer.start(
            1000
        )

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
                    f"{hours}h {minutes}m active"
                )

            else:

                text = (
                    f"{hours}h active"
                )

        self.duration_label.setText(
            text
        )