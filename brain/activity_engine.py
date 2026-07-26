from brain.context import context
from brain.activity import activity
from brain.event_bus import bus
from brain.activity_history import activity_history


class ActivityEngine:

    def __init__(self):

        bus.subscribe(
            "window_changed",
            self.on_window_changed
        )

    def on_window_changed(
        self,
        data
    ):

        title = data["title"].lower()

        if any(
            word in title
            for word in (
                "visual studio",
                "vscode",
                "code",
                "powershell",
                "terminal",
                "cmd",
                "git"
            )
        ):

            activity.update(
                "Coding",
                95,
                [context.current_window]
            )
            
            activity_history.add(
                activity.name
            )

        elif any(
            word in title
            for word in (
                "chrome",
                "edge",
                "firefox"
            )
        ):

            activity.update(
                "Browsing",
                80,
                [context.current_window]
            )
            activity_history.add(
                activity.name
            )
            
            
        elif any(
            word in title
            for word in (
                "spotify",
                "music"
            )
        ):

            activity.update(
                "Listening to Music",
                100,
                [context.current_window]
            )
            
            activity_history.add(
                activity.name
            )

        else:

            activity.update(
                "Unknown",
                20,
                [context.current_window]
            )
            
            activity_history.add(
                activity.name
            )

        recent = activity_history.recent()[-5:]

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