

import time

from PySide6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QGraphicsOpacityEffect,
    QSizePolicy,
)

import widgets.theme as theme


class ActivityCard(QWidget):
    """
    Live desktop-activity surface for DraxAgent.

    The card intentionally stays presentation-only:
        - receives activity state
        - renders useful context
        - tracks elapsed time
        - exposes confidence
        - keeps the visual transition lightweight

    Public API kept compatible with the existing GUI:
        update_activity(
            activity_name,
            application,
            window_title,
            started_at,
            context=""
        )
    """

    def __init__(self):
        super().__init__()

        self.current_window_started = None
        self.current_activity = None
        self.current_application = None
        self.current_process = None
        self.current_window_title = ""
        self.current_context = ""
        self.current_confidence = 0

        self._last_payload_key = None
        self._details_visible = False

        self.build_ui()
        self._build_animations()

        # Duration is cheap and local, so a 1-second GUI timer is fine.
        self.duration_timer = QTimer(self)
        self.duration_timer.setInterval(1000)
        self.duration_timer.timeout.connect(self.update_duration)

        self.update_duration()

    # ============================================================
    # UI
    # ============================================================

    def build_ui(self):

        outer_layout = QHBoxLayout(self)

        outer_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        outer_layout.setSpacing(0)

        # --------------------------------------------------------
        # Accent rail
        # --------------------------------------------------------

        self.accent_rail = QFrame()

        self.accent_rail.setFixedWidth(3)

        self.accent_rail.setStyleSheet(
            f"""
            background: {theme.ACCENT};
            border: none;
            border-radius: 2px;
            """
        )

        outer_layout.addWidget(self.accent_rail)

        # --------------------------------------------------------
        # Card
        # --------------------------------------------------------

        self.card = QFrame()

        self.card.setObjectName("activityCard")

        self.card.setStyleSheet(
            f"""
            QFrame#activityCard {{
                background: {theme.STATUS_BUBBLE};
                border: 1px solid {theme.STATUS_BORDER};
                border-left: none;
                border-radius: 0px 14px 14px 0px;
            }}
            """
        )

        outer_layout.addWidget(self.card, 1)

        card_layout = QVBoxLayout(self.card)

        card_layout.setContentsMargins(
            15,
            10,
            15,
            10,
        )

        card_layout.setSpacing(6)

        # --------------------------------------------------------
        # Header
        # --------------------------------------------------------

        header = QHBoxLayout()

        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(6)

        self.indicator = QLabel("●")

        self.indicator.setFixedWidth(8)
        self.indicator.setAlignment(Qt.AlignCenter)

        self.indicator.setStyleSheet(
            f"""
            color: {theme.SUCCESS};
            font-size: 8px;
            background: transparent;
            border: none;
            """
        )

        header.addWidget(self.indicator)

        self.header_label = QLabel("CURRENTLY")

        self.header_label.setStyleSheet(
            f"""
            color: {theme.TEXT_MUTED};
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 1px;
            background: transparent;
            border: none;
            """
        )

        header.addWidget(self.header_label)

        header.addStretch()

        self.confidence_label = QLabel("—")

        self.confidence_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        self.confidence_label.setStyleSheet(
            f"""
            color: {theme.TEXT_MUTED};
            font-size: 9px;
            font-weight: 600;
            background: transparent;
            border: none;
            """
        )

        header.addWidget(self.confidence_label)

        self.live_label = QLabel("LIVE")

        self.live_label.setStyleSheet(
            f"""
            color: {theme.SUCCESS};
            font-size: 8px;
            font-weight: 700;
            background: transparent;
            border: none;
            """
        )

        header.addWidget(self.live_label)

        card_layout.addLayout(header)

        # --------------------------------------------------------
        # Main content
        # --------------------------------------------------------

        self.content_container = QWidget()

        self.content_container.setStyleSheet(
            """
            background: transparent;
            border: none;
            """
        )

        content_layout = QVBoxLayout(self.content_container)

        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(3)

        # Activity + duration

        activity_row = QHBoxLayout()

        activity_row.setContentsMargins(0, 0, 0, 0)
        activity_row.setSpacing(10)

        self.activity_label = QLabel("Ready")

        self.activity_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        self.activity_label.setStyleSheet(
            f"""
            color: {theme.TEXT};
            font-size: 16px;
            font-weight: 700;
            background: transparent;
            border: none;
            """
        )

        self.activity_label.setToolTip(
            "Drax's current interpretation of what you're doing."
        )

        activity_row.addWidget(self.activity_label, 1)

        self.duration_label = QLabel("Just now")

        self.duration_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        self.duration_label.setMinimumWidth(78)

        self.duration_label.setStyleSheet(
            f"""
            color: {theme.TEXT_MUTED};
            font-size: 10px;
            font-weight: 500;
            background: transparent;
            border: none;
            """
        )

        activity_row.addWidget(self.duration_label)

        content_layout.addLayout(activity_row)

        # --------------------------------------------------------
        # Application
        # --------------------------------------------------------

        application_row = QHBoxLayout()

        application_row.setContentsMargins(0, 0, 0, 0)
        application_row.setSpacing(6)

        self.application_marker = QLabel("▸")

        self.application_marker.setFixedWidth(8)

        self.application_marker.setAlignment(
            Qt.AlignCenter
        )

        self.application_marker.setStyleSheet(
            f"""
            color: {theme.ACCENT};
            font-size: 10px;
            font-weight: 700;
            background: transparent;
            border: none;
            """
        )

        application_row.addWidget(self.application_marker)

        self.application_label = QLabel(
            "Waiting for activity..."
        )

        self.application_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        self.application_label.setWordWrap(False)

        self.application_label.setTextInteractionFlags(
            Qt.NoTextInteraction
        )

        self.application_label.setStyleSheet(
            f"""
            color: {theme.TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 500;
            background: transparent;
            border: none;
            """
        )

        application_row.addWidget(
            self.application_label,
            1,
        )

        content_layout.addLayout(application_row)

        # --------------------------------------------------------
        # Window title / exact context
        # --------------------------------------------------------

        self.window_label = QLabel("")

        self.window_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        self.window_label.setWordWrap(False)

        self.window_label.setTextInteractionFlags(
            Qt.NoTextInteraction
        )

        self.window_label.setStyleSheet(
            f"""
            color: {theme.TEXT_MUTED};
            font-size: 10px;
            font-weight: 400;
            background: transparent;
            border: none;
            """
        )

        self.window_label.hide()

        content_layout.addWidget(self.window_label)

        # --------------------------------------------------------
        # Drax interpretation
        # --------------------------------------------------------

        self.context_label = QLabel("")

        self.context_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        self.context_label.setWordWrap(False)

        self.context_label.setTextInteractionFlags(
            Qt.NoTextInteraction
        )

        self.context_label.setStyleSheet(
            f"""
            color: {theme.TEXT_MUTED};
            font-size: 10px;
            font-weight: 400;
            font-style: italic;
            background: transparent;
            border: none;
            """
        )

        self.context_label.hide()

        content_layout.addWidget(self.context_label)

        card_layout.addWidget(self.content_container)

        # --------------------------------------------------------
        # Confidence meter
        # --------------------------------------------------------

        confidence_row = QHBoxLayout()

        confidence_row.setContentsMargins(0, 1, 0, 0)
        confidence_row.setSpacing(6)

        confidence_caption = QLabel("CONFIDENCE")

        confidence_caption.setStyleSheet(
            f"""
            color: {theme.TEXT_MUTED};
            font-size: 8px;
            font-weight: 700;
            background: transparent;
            border: none;
            """
        )

        confidence_row.addWidget(confidence_caption)

        self.confidence_track = QFrame()

        self.confidence_track.setFixedHeight(3)
        self.confidence_track.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        self.confidence_track.setStyleSheet(
            f"""
            QFrame {{
                background: {theme.STATUS_BORDER};
                border: none;
                border-radius: 2px;
            }}
            """
        )

        self.confidence_fill = QFrame(
            self.confidence_track
        )

        self.confidence_fill.setGeometry(
            0,
            0,
            0,
            3,
        )

        self.confidence_fill.setStyleSheet(
            f"""
            background: {theme.ACCENT};
            border: none;
            border-radius: 2px;
            """
        )

        confidence_row.addWidget(
            self.confidence_track,
            1,
        )

        self.confidence_value = QLabel("—")

        self.confidence_value.setFixedWidth(32)

        self.confidence_value.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        self.confidence_value.setStyleSheet(
            f"""
            color: {theme.TEXT_MUTED};
            font-size: 8px;
            font-weight: 600;
            background: transparent;
            border: none;
            """
        )

        confidence_row.addWidget(self.confidence_value)

        card_layout.addLayout(confidence_row)

        # --------------------------------------------------------
        # Bottom separator
        # --------------------------------------------------------

        self.separator = QFrame()

        self.separator.setFixedHeight(1)

        self.separator.setStyleSheet(
            f"""
            background: {theme.STATUS_BORDER};
            border: none;
            """
        )

        card_layout.addSpacing(1)
        card_layout.addWidget(self.separator)

        # --------------------------------------------------------
        # Sizing
        # --------------------------------------------------------

        self.setMinimumHeight(112)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        # Useful hover information without adding another button.
        self.setToolTip(
            "Live desktop activity detected by Drax."
        )

    # ============================================================
    # ANIMATIONS
    # ============================================================

    def _build_animations(self):

        # --------------------------------------------------------
        # Content transition
        #
        # IMPORTANT:
        # Only run this when the activity identity actually changes.
        # Repeated classifier updates do not cause flicker.
        # --------------------------------------------------------

        self.content_opacity = QGraphicsOpacityEffect(
            self.content_container
        )

        self.content_container.setGraphicsEffect(
            self.content_opacity
        )

        self.content_opacity.setOpacity(1.0)

        self.content_fade = QPropertyAnimation(
            self.content_opacity,
            b"opacity",
            self,
        )

        self.content_fade.setDuration(160)

        self.content_fade.setEasingCurve(
            QEasingCurve.OutCubic
        )

        # --------------------------------------------------------
        # Live indicator pulse
        # --------------------------------------------------------

        self.indicator_opacity = QGraphicsOpacityEffect(
            self.indicator
        )

        self.indicator.setGraphicsEffect(
            self.indicator_opacity
        )

        self.indicator_pulse = QPropertyAnimation(
            self.indicator_opacity,
            b"opacity",
            self,
        )

        self.indicator_pulse.setDuration(1400)

        self.indicator_pulse.setStartValue(1.0)
        self.indicator_pulse.setKeyValueAt(0.5, 0.42)
        self.indicator_pulse.setEndValue(1.0)

        self.indicator_pulse.setEasingCurve(
            QEasingCurve.InOutSine
        )

        self.indicator_pulse.setLoopCount(-1)
        self.indicator_pulse.start()

    # ============================================================
    # UPDATE
    # ============================================================

    def update_activity(
        self,
        activity_name,
        application,
        window_title,
        started_at,
        context="",
        confidence=None,
        process=None,
    ):
        """
        Update the card.

        `confidence` and `process` are optional so the existing GUI can
        keep calling the original five-argument API. Newer callers can
        provide them for richer rendering.
        """

        activity_name = self._clean(
            activity_name,
            "Unknown",
        )

        application = self._clean(
            application,
            "Unknown application",
        )

        window_title = self._clean(
            window_title,
            "",
        )

        context = self._clean(
            context,
            "",
        )

        if confidence is None:
            confidence = self.current_confidence

        try:
            confidence = int(confidence)
        except (TypeError, ValueError):
            confidence = 0

        confidence = max(0, min(100, confidence))

        process = self._clean(
            process,
            "",
        )

        payload_key = (
            activity_name,
            application,
            window_title,
            context,
            confidence,
            process,
        )

        activity_changed = (
            activity_name != self.current_activity
            or application != self.current_application
            or process != self.current_process
        )

        self.current_activity = activity_name
        self.current_application = application
        self.current_process = process
        self.current_window_title = window_title
        self.current_context = context
        self.current_confidence = confidence

        # --------------------------------------------------------
        # Timing
        # --------------------------------------------------------

        if started_at is not None:
            try:
                started_at = float(started_at)
            except (TypeError, ValueError):
                started_at = time.time()
        else:
            started_at = time.time()

        self.current_window_started = started_at

        # --------------------------------------------------------
        # Avoid redundant visual work.
        # --------------------------------------------------------

        if payload_key == self._last_payload_key:
            self.update_duration()
            return

        self._last_payload_key = payload_key

        # --------------------------------------------------------
        # Render
        # --------------------------------------------------------

        self.activity_label.setText(activity_name)
        self.application_label.setText(application)

        self._set_window_title(window_title)
        self._set_context(context)

        self._set_confidence(confidence)

        # A long exact title remains available through the tooltip.
        tooltip_parts = [
            f"Activity: {activity_name}",
            f"Application: {application}",
        ]

        if process:
            tooltip_parts.append(
                f"Process: {process}"
            )

        if window_title:
            tooltip_parts.append(
                f"Window: {window_title}"
            )

        if context:
            tooltip_parts.append(
                f"Drax: {context}"
            )

        self.setToolTip(
            "\n".join(tooltip_parts)
        )

        self.update_duration()
        self.duration_timer.start()

        # --------------------------------------------------------
        # Lightweight transition only on actual activity changes.
        # --------------------------------------------------------

        if activity_changed:
            self._animate_content_change()

    # ============================================================
    # RENDER HELPERS
    # ============================================================

    @staticmethod
    def _clean(value, fallback=""):
        if value is None:
            return fallback

        value = str(value).strip()

        return value if value else fallback

    def _set_window_title(self, title):

        if not title:
            self.window_label.clear()
            self.window_label.hide()
            return

        self.window_label.setText(
            f"Window  ·  {title}"
        )

        self.window_label.setToolTip(title)
        self.window_label.show()

    def _set_context(self, context):

        if not context:
            self.context_label.clear()
            self.context_label.hide()
            return

        self.context_label.setText(
            f"Drax  ·  {context}"
        )

        self.context_label.setToolTip(context)
        self.context_label.show()

    def _set_confidence(self, confidence):

        self.confidence_label.setText(
            f"{confidence}%"
        )

        self.confidence_value.setText(
            f"{confidence}%"
        )

        self.confidence_fill.setGeometry(
            0,
            0,
            int(
                self.confidence_track.width()
                * confidence
                / 100
            ),
            3,
        )

        if confidence >= 80:
            label = "High confidence"
        elif confidence >= 55:
            label = "Moderate confidence"
        elif confidence > 0:
            label = "Low confidence"
        else:
            label = "No confidence data"

        self.confidence_label.setToolTip(label)
        self.confidence_track.setToolTip(label)

    def _animate_content_change(self):

        if self.content_fade.state():
            self.content_fade.stop()

        self.content_opacity.setOpacity(0.70)

        self.content_fade.setStartValue(0.70)
        self.content_fade.setEndValue(1.0)

        self.content_fade.start()

    # ============================================================
    # DURATION
    # ============================================================

    def update_duration(self):

        if self.current_window_started is None:
            self.duration_label.setText("Just now")
            return

        elapsed = max(
            0,
            int(
                time.time()
                - self.current_window_started
            ),
        )

        if elapsed < 60:
            text = "Just now"

        elif elapsed < 3600:
            minutes = elapsed // 60

            text = (
                f"{minutes} minute"
                if minutes == 1
                else f"{minutes} minutes"
            )

            text += " active"

        else:
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60

            if minutes:
                text = f"{hours}h {minutes}m active"
            else:
                text = f"{hours}h active"

        self.duration_label.setText(text)

    # ============================================================
    # RESIZE
    # ============================================================

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self._resize_confidence_fill()

    def _resize_confidence_fill(self):

        if not hasattr(self, "confidence_track"):
            return

        confidence = self.current_confidence

        self.confidence_fill.setGeometry(
            0,
            0,
            int(
                self.confidence_track.width()
                * confidence
                / 100
            ),
            3,
        )
