from brain.context import context
from brain.memory import memory
from brain.desktop_state import desktop_state
from brain.experience import experience
from brain.activity import activity


class Awareness:

    def snapshot(self):

        # -------------------------------------------------
        # Drax itself is intentionally excluded from the
        # tracked desktop activity. When the user opens the
        # Drax window to ask a question, context.current_* may
        # briefly point at Drax even though the user's real
        # task is still the external application.
        #
        # In that case, fall back to the last accepted activity
        # state instead of teaching Drax that the user is
        # "working in Drax" simply because they summoned it.
        # -------------------------------------------------

        application = context.current_application
        process = context.current_process
        window = context.current_window

        application_text = (
            application
            or ""
        ).lower()

        process_text = (
            process
            or ""
        ).lower()

        drax_foreground = (
            "drax" in application_text
            or "draxagent" in application_text
            or process_text in {
                "python.exe",
                "python3.exe",
                "python3.11",
                "python3.11.exe",
            }
        )

        if drax_foreground:

            application = (
                activity.application
                or application
            )

            process = (
                activity.process
                or process
            )

            if activity.windows:
                window = activity.windows[-1]

        return {

            # -------------------------------------------------
            # Live desktop state
            # -------------------------------------------------
            # These fields are intentionally explicit so higher
            # layers can reason about the user's current context
            # without scraping UI text.

            "current_application": application,

            "current_process": process,

            "current_window": window,

            "activity": activity.name,

            "activity_confidence": activity.confidence,

            "activity_started_at": activity.started_at,

            "recent_memory": memory.get_recent(5),

            "recent_sessions": experience.recent()[-5:],

            "foreground": desktop_state.foreground,

            "drax_foreground": drax_foreground,

        }


awareness = Awareness()