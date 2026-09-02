from brain.context import context
from brain.activity import activity
from brain.event_bus import bus
from brain.activity_history import activity_history

from brain.intelligence.activity_classifier import (
    activity_classifier
)


class ActivityEngine:

    def __init__(self):
        self._latest_context = None

        bus.subscribe(
            "window_changed",
            self.on_window_changed
        )

    # =================================
    # DraxAgent detection
    # =================================

    def is_drax_window(
        self,
        application,
        process
    ):
        application_value = (
            application
            or ""
        ).lower()

        process_value = (
            process
            or ""
        ).lower()

        if (
            "draxagent" in application_value
            or "drax" in application_value
        ):
            return True

        if process_value in {
            "python.exe",
            "python3.exe",
            "python3.11",
            "python3.11.exe",
        }:
            return True

        return False

    # =================================
    # Window changed
    # =================================

    def on_window_changed(
        self,
        data
    ):
        if not isinstance(data, dict):
            return

        application = data.get(
            "application"
        )

        process = data.get(
            "process"
        )

        # ---------------------------------
        # Ignore DraxAgent itself
        # ---------------------------------

        if self.is_drax_window(
            application,
            process
        ):
            return

        # ---------------------------------
        # Build intelligence context
        # ---------------------------------

        context_data = {
            "application": application,
            "process": process,
            "executable": data.get(
                "executable"
            ),
            "window_title": data.get(
                "title"
            ),
        }

        # Keep the exact context associated
        # with this classification request.
        #
        # This is important because classification
        # happens asynchronously and the foreground
        # window may change while the model is thinking.

        self._latest_context = dict(
            context_data
        )

        # ---------------------------------
        # Ask intelligence layer
        #
        # Classification is asynchronous.
        # Observer remains responsive.
        # ---------------------------------

        activity_classifier.classify_async(
            context_data,
            self.on_activity_classified
        )

    # =================================
    # Intelligence result
    # =================================

    def on_activity_classified(
        self,
        result
    ):
        if not isinstance(result, dict):
            result = {}

        activity_name = str(
            result.get(
                "activity",
                "Unknown"
            )
        ).strip()

        if not activity_name:
            activity_name = "Unknown"

        confidence = result.get(
            "confidence",
            20
        )

        try:
            confidence = int(
                confidence
            )
        except (
            TypeError,
            ValueError
        ):
            confidence = 20

        confidence = max(
            0,
            min(
                confidence,
                100
            )
        )

        # ---------------------------------
        # Use the context belonging to the
        # classification request.
        #
        # ActivityClassifier already prevents
        # stale generations from reaching this
        # callback, so this remains synchronized
        # with the latest accepted result.
        # ---------------------------------

        current_application = (
            context.current_application
        )

        current_process = (
            context.current_process
        )

        current_window = (
            context.current_window
        )

        # ---------------------------------
        # Update activity state
        # ---------------------------------

        activity.update(
            activity_name,
            confidence,
            [
                current_window
            ],
            application=current_application,
            process=current_process
        )

        # ---------------------------------
        # Activity history
        # ---------------------------------

        activity_history.add(
            activity.name
        )

        # ---------------------------------
        # Build UI-safe activity payload
        #
        # Keep this deliberately presentation-
        # neutral. The ActivityCard decides how
        # this information should look.
        # ---------------------------------

        activity_payload = {
            "activity": activity.name,
            "confidence": activity.confidence,
            "application": activity.application,
            "process": activity.process,
            "window": current_window,
            "started_at": activity.started_at,

            # Optional richer context.
            #
            # The classifier may provide this in
            # the future. Older classifier results
            # simply leave it empty.
            "context": result.get(
                "context",
                ""
            ),

            # Preserve any future metadata without
            # forcing the UI to depend on it.
            "visual_context": result.get(
                "visual_context"
            ),
        }

        # ---------------------------------
        # Notify UI
        # ---------------------------------

        bus.emit(
            "activity_updated",
            activity_payload
        )

        # ---------------------------------
        # Debug timeline
        # ---------------------------------

        recent = (
            activity_history.recent()[-5:]
        )

        print(
            "\n===== Activity Timeline ====="
        )

        for item in recent:
            print(
                item["activity"]
            )

        print(
            "=============================\n"
        )


activity_engine = ActivityEngine()