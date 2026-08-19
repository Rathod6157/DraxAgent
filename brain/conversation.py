from core import understand
from executor import execute

from brain.companion import companion


class ConversationEngine:

    def __init__(self):

        self.pending = None

    def _handle_pending(self, message):

        if not self.pending:
            return None

        pending = self.pending

        handler = pending.get("handler")

        if not handler:
            self.pending = None
            return None

        result = handler(
            pending["data"],
            message
        )

        # Handler may return another pending state.
        if result:
            self.pending = {
                "handler": handler,
                "data": result
            }

            return result

        # Operation finished / cancelled.
        self.pending = None

        return None


    def process(
        self,
        message
    ):

        message = message.strip()

        if not message:
            return None

        # ---------------------------------
        # Pending operation
        # ---------------------------------

        if self.pending:

            result = self._handle_pending(
                message
            )

            if result is not None:

                return companion.chat(
                    message,
                    execution={
                        "handled": True,
                        "success": True,
                        "message": "",
                        "data": result
                    }
                )

            # Pending operation finished.
            # Don't interpret "yes"/"no" as a new command.
            return None

        # ---------------------------------
        # Normal command
        # ---------------------------------

        task = understand(message)

        result = execute(task)

        # ---------------------------------
        # Check for pending skill action
        # ---------------------------------

        if result.data.get("pending"):

            pending = result.data["pending"]

            self.pending = {
                "handler": pending["handler"],
                "data": pending["data"]
            }

            return result.message

        # ---------------------------------
        # Compound command
        # ---------------------------------

        if task.intent == "compound":

            action_results = result.data.get(
                "results",
                []
            )

            conversation_tasks = result.data.get(
                "conversation_tasks",
                []
            )

            completed_actions = []

            for item in action_results:

                child_task = item["task"]
                child_result = item["result"]

                completed_actions.append({
                    "intent": child_task.intent,
                    "target": child_task.target,
                    "success": child_result.success,
                    "message": child_result.message
                })

            if conversation_tasks:

                conversation_text = " ".join(
                    child.data.get(
                        "raw_command",
                        ""
                    )
                    for child in conversation_tasks
                )

                return companion.chat(
                    message,
                    execution={
                        "success": result.success,
                        "actions": completed_actions,
                        "conversation": conversation_text
                    }
                )

            return result

        # ---------------------------------
        # Normal request
        # ---------------------------------

        if result.handled:

            return result

        return companion.chat(
            message,
            execution={
                "handled": result.handled,
                "success": result.success,
                "message": result.message,
                "data": result.data
            }
        )


conversation = ConversationEngine()