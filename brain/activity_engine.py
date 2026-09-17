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


    # ========================================================
    # DRAX DETECTION
    # ========================================================

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


    # ========================================================
    # WINDOW CHANGED
    # ========================================================

    def on_window_changed(
        self,
        data
    ):

        if not isinstance(
            data,
            dict
        ):

            return


        application = (
            data.get("application")
            or "Unknown application"
        )

        process = (
            data.get("process")
            or ""
        )

        window_title = (
            data.get("title")
            or data.get("window")
            or ""
        )


        # ----------------------------------------------------
        # Ignore Drax itself
        # ----------------------------------------------------

        if self.is_drax_window(
            application,
            process
        ):

            return


        # ----------------------------------------------------
        # Build immutable observation context
        # ----------------------------------------------------

        request_context = {

            "application":
                str(application),

            "process":
                str(process),

            "executable":
                data.get("executable"),

            "window_title":
                str(window_title),

        }


        self._latest_context = dict(
            request_context
        )


        # ====================================================
        # FAST PATH
        # ====================================================
        #
        # The UI should NOT wait for Gemini.
        #
        # Immediately tell the frontend:
        #
        #     Using Chrome
        #
        # Then AI can refine it later:
        #
        #     Browsing
        #
        # ====================================================

        bus.emit(
            "activity_context",
            {
                "application":
                    application,

                "process":
                    process,

                "window":
                    window_title,

                "executable":
                    data.get(
                        "executable"
                    ),

                "observed_at":
                    data.get(
                        "timestamp"
                    )
                    or time.time(),
            }
        )


        # ====================================================
        # GENERATION
        # ====================================================

        self._generation += 1

        generation = (
            self._generation
        )


        # ====================================================
        # AI CLASSIFICATION
        # ====================================================

        activity_classifier.classify_async(

            dict(
                request_context
            ),

            lambda result,
                   request=request_context,
                   request_generation=generation:

                self.on_activity_classified(
                    result,
                    request,
                    request_generation
                )
        )


    # ========================================================
    # CLASSIFIER RESULT
    # ========================================================

    def on_activity_classified(
        self,
        result,
        request_context=None,
        request_generation=None
    ):

        if not isinstance(
            result,
            dict
        ):

            result = {}


        # ----------------------------------------------------
        # Reject stale AI result
        # ----------------------------------------------------

        if (
            request_generation is not None
            and request_generation != self._generation
        ):

            return


        request_context = (

            request_context

            if isinstance(
                request_context,
                dict
            )

            else {}
        )


        # ----------------------------------------------------
        # Activity
        # ----------------------------------------------------

        activity_name = str(

            result.get(
                "activity",
                "Unknown"
            )

        ).strip()


        if not activity_name:

            activity_name = "Unknown"


        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Use the context that produced THIS result.
        #
        # Never read the mutable global desktop state here.
        # ----------------------------------------------------

        application = (

            request_context.get(
                "application"
            )

            or context.current_application
            or "Unknown application"
        )


        process = (

            request_context.get(
                "process"
            )

            or context.current_process
            or ""
        )


        window = (

            request_context.get(
                "window_title"
            )

            or context.current_window
            or ""
        )


        # ====================================================
        # UPDATE SHARED ACTIVITY
        # ====================================================

        activity.update(

            activity_name,

            confidence,

            [
                window
            ],

            application=application,

            process=process
        )


        # ====================================================
        # HISTORY
        # ====================================================

        activity_history.add(
            activity.name
        )


        # ====================================================
        # UI PAYLOAD
        # ====================================================

        activity_payload = {

            "activity":
                activity.name,

            "confidence":
                activity.confidence,

            "application":
                activity.application,

            "process":
                activity.process,

            "window":
                window,

            "started_at":
                activity.started_at,

            "context":
                result.get(
                    "context",
                    ""
                ),

            "visual_context":
                result.get(
                    "visual_context"
                ),
        }


        # ====================================================
        # FRONTEND
        # ====================================================

        bus.emit(
            "activity_updated",
            activity_payload
        )


        # ====================================================
        # DEBUG TIMELINE
        # ====================================================

        recent = (
            activity_history
            .recent()
            [-5:]
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


# ============================================================
# SINGLETON
# ============================================================

activity_engine = ActivityEngine()