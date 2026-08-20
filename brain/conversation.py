from core import understand
from executor import execute

from brain.companion import companion

from skills.open_app import (
    handle_pending_response as handle_open_pending
)

from skills.close_app import (
    handle_pending_response as handle_close_pending
)


class ConversationEngine:

    def __init__(self):

        self.pending_action = None


    def process(
        self,
        message
    ):

        # ---------------------------------
        # Pending action
        # ---------------------------------

        if self.pending_action:

            status = self.pending_action.get(
                "status"
            )

            if status == "close_confirmation_required":

                self.pending_action = (
                    handle_close_pending(
                        self.pending_action,
                        message
                    )
                )

                return


            self.pending_action = (
                handle_open_pending(
                    self.pending_action,
                    message
                )
            )

            return


        # ---------------------------------
        # Understand request
        # ---------------------------------

        task = understand(
            message
        )

        result = execute(
            task
        )


        # ---------------------------------
        # Store pending action
        # ---------------------------------

        if isinstance(
            result,
            dict
        ):

            status = result.get(
                "status"
            )

            if status in {
                "confirmation_required",
                "selection_required",
                "close_confirmation_required"
            }:

                self.pending_action = result

                return


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