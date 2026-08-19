from brain import bus
from core import understand


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

        task = understand(message)

        print(
            f"[Decision] Intent: {task.intent}"
        )

        if task.intent == "compound":

            parts = task.data.get(
                "tasks",
                []
            )

            print(
                f"[Decision] Compound command: "
                f"{len(parts)} parts"
            )

            for index, child in enumerate(
                parts,
                start=1
            ):

                print(
                    f"  {index}. "
                    f"{child.intent}: "
                    f"{child.data.get('raw_command', '')}"
                )


decision = DecisionEngine()