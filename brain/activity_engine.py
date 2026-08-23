from brain.context import context
from brain.activity import activity
from brain.event_bus import bus
from brain.activity_history import activity_history


class ActivityEngine:

    # ---------------------------------
    # Application → Activity rules
    # ---------------------------------

    ACTIVITY_RULES = {

        "coding": {
            "applications": {
                "Code.exe",
                "code.exe",
                "Visual Studio Code",
                "PyCharm",
                "Sublime Text",
                "Notepad++",
            },
            "confidence": 95
        },

        "browsing": {
            "applications": {
                "chrome.exe",
                "msedge.exe",
                "firefox.exe",
                "Google Chrome",
                "Microsoft Edge",
                "Mozilla Firefox",
            },
            "confidence": 80
        },

        "music": {
            "applications": {
                "spotify.exe",
                "Spotify",
            },
            "confidence": 100
        },

        "file_management": {
            "applications": {
                "explorer.exe",
                "File Explorer",
            },
            "confidence": 85
        },

        "terminal": {
            "applications": {
                "powershell.exe",
                "cmd.exe",
                "Windows Terminal",
                "WindowsTerminal.exe",
            },
            "confidence": 90
        },
    }


    # ---------------------------------
    # Friendly activity names
    # ---------------------------------

    ACTIVITY_NAMES = {

        "coding":
            "Coding",

        "browsing":
            "Browsing",

        "music":
            "Listening to Music",

        "file_management":
            "File Management",

        "terminal":
            "Using Terminal",
    }


    def __init__(self):

        bus.subscribe(
            "window_changed",
            self.on_window_changed
        )


    def classify(
        self,
        application,
        process
    ):

        application_value = (
            application
            or ""
        )

        process_value = (
            process
            or ""
        )


        for rule_name, rule in (
            self.ACTIVITY_RULES.items()
        ):

            applications = rule[
                "applications"
            ]


            if (
                application_value in applications
                or process_value in applications
            ):

                return (
                    self.ACTIVITY_NAMES[
                        rule_name
                    ],
                    rule["confidence"]
                )


        return (
            "Unknown",
            20
        )


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


        # ---------------------------------
        # DraxAgent / Python itself
        # ---------------------------------

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
        #
        # When DraxAgent becomes foreground,
        # Windows reports Python as the active
        # process. We don't want that to destroy
        # the user's previous meaningful activity.
        #

        if self.is_drax_window(
            application,
            process
        ):

            return


        # ---------------------------------
        # Classify real user activity
        # ---------------------------------

        activity_name, confidence = (
            self.classify(
                application,
                process
            )
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
            application=application,
            process=process
        )


        activity_history.add(
            activity.name
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