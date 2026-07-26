from brain import bus


class DecisionEngine:

    def __init__(self):

        bus.subscribe(
            "message",
            self.process
        )

    def process(
        self,
        message
    ):

        text = message.lower()

        if "open" in text:

            print(
                "[Decision] Intent: open_application"
            )

        elif "close" in text:

            print(
                "[Decision] Intent: close_application"
            )

        elif "timer" in text:

            print(
                "[Decision] Intent: timer"
            )

        else:

            print(
                "[Decision] Intent: conversation"
            )


decision = DecisionEngine()