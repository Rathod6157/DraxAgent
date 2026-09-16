import time

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
        self._generation = 0

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

        # Keep the exact context associated with this
        # observation. Classification happens asynchronously,
        # so never rely on the mutable global context when the
        # classifier eventually returns.
        self._latest_context = dict(
            context_data
        )

        # ---------------------------------
        # FAST PATH: desktop context
        # ---------------------------------
        #
        # The user should see an application switch immediately.
        # Semantic activity classification may take longer because
        # it can involve AI/screenshot work. We therefore publish
        # the raw desktop observation first, then let the classifier
        # upgrade it a moment later.
        #
        # This gives the UI a two-stage experience:
        #
        #   instant -> Using Microsoft Edge
        #   refined -> Debugging Software Code
        #
        bus.emit(
            "activity_context",
            {
                "application": application,
                "process": process,
                "window": context_data.get("window_title"),
                "executable": context_data.get("executable"),
                "observed_at": time.time(),
            }
        )

        # ---------------------------------
        # AI classification
        # ---------------------------------
        #
        # Capture the request context in the callback so a slow
        # classifier can never render the wrong window.
        # ---------------------------------

        request_context = dict(
            context_data
        )

        # Every foreground observation gets its own generation.
        # If the classifier is slower than the user switching windows,
        # an older result is discarded instead of repainting the card
        # with stale information.
        self._generation += 1
        generation = self._generation

        activity_classifier.classify_async(
            request_context,
            lambda result, request=request_context,
                   request_generation=generation:
            self.on_activity_classified(
                result,
                request,
                request_generation
            )
        )

    # =================================
    # Intelligence result
    # =================================

    def on_activity_classified(
        self,
        result,
        request_context=None,
        request_generation=None
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

        request_context = (
            request_context
            if isinstance(request_context, dict)
            else {}
        )

        # Never allow an old classifier response to overwrite the
        # activity belonging to a newer foreground window.
        if (
            request_generation is not None
            and request_generation != self._generation
        ):
            return

        current_application = (
            request_context.get("application")
            or context.current_application
        )

        current_process = (
            request_context.get("process")
            or context.current_process
        )

        current_window = (
            request_context.get("window_title")
            or context.current_window
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