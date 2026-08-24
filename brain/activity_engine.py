from brain.context import context
from brain.activity import activity
from brain.event_bus import bus
from brain.activity_history import activity_history

from brain.intelligence.activity_classifier import (
    activity_classifier
)


class ActivityEngine:

    def __init__(self):

        bus.subscribe(
            "window_changed",
            self.on_window_changed
        )


    # ---------------------------------
    # DraxAgent detection
    # ---------------------------------

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


    # ---------------------------------
    # Window changed
    # ---------------------------------

    def on_window_changed(
        self,
        data
    ):

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


    # ---------------------------------
    # Intelligence result
    # ---------------------------------

    def on_activity_classified(
        self,
        result
    ):

        activity_name = result.get(
            "activity",
            "Unknown"
        )

        confidence = result.get(
            "confidence",
            20
        )


        # ---------------------------------
        # Update activity state
        # ---------------------------------

        activity.update(
            activity_name,
            confidence,
            [
                context.current_window
            ],
            application=context.current_application,
            process=context.current_process
        )


        # ---------------------------------
        # Activity history
        # ---------------------------------

        activity_history.add(
            activity.name
        )
        
        bus.emit(
            "activity_updated",
            {
                "activity": activity.name,
                "confidence": activity.confidence,
                "application": activity.application,
                "process": activity.process,
                "window": context.current_window,
                "started_at": activity.started_at
            }
        )


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