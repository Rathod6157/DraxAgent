import time


class DesktopState:

    def __init__(self):

        self.foreground = None

        self.background = {}

        self.history = []


    def set_foreground(
        self,
        window
    ):

        self.foreground = window

        self.history.append(
            {
                "window": window,
                "time": time.time()
            }
        )

        self.history = self.history[-50:]


    def update_background(
        self,
        name
    ):

        self.background[name] = time.time()


    @property
    def recent(self):

        return self.history[-10:]


    def current(self):

        return {

            "foreground":
                self.foreground,

            "background":
                self.background,

            "recent":
                self.recent

        }


    def debug(self):

        print(
            "\n===== Desktop State ====="
        )


        if self.foreground:

            print(
                "Application:",
                self.foreground.get(
                    "application",
                    "Unknown"
                )
            )

            print(
                "Process:",
                self.foreground.get(
                    "process",
                    "Unknown"
                )
            )

            print(
                "PID:",
                self.foreground.get(
                    "pid",
                    "Unknown"
                )
            )

            print(
                "Foreground:",
                self.foreground.get(
                    "title",
                    "Unknown"
                )
            )

        else:

            print(
                "Foreground: Unknown"
            )


        print()

        print("Recent:")

        for item in self.recent:

            window = item["window"]

            if isinstance(
                window,
                dict
            ):

                print(
                    "-",
                    window.get(
                        "title",
                        "Unknown"
                    ),
                    "(",
                    window.get(
                        "process",
                        "Unknown"
                    ),
                    ")"
                )

            else:

                print(
                    "-",
                    window
                )


        print(
            "=========================\n"
        )


desktop_state = DesktopState()