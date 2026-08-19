from core import understand
from executor import execute

from brain.companion import companion


class ConversationEngine:

    def process(
        self,
        message
    ):

        task = understand(message)

        result = execute(task)

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

            # If the compound command contains
            # something conversational, let Drax
            # respond to that part.
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

            # Pure action compound command.
            # The skills already handled everything.
            return result

        # ---------------------------------
        # Normal request
        # ---------------------------------

        # If a skill successfully handled the request,
        # DO NOT send it to Gemini again.
        if result.handled:

            return result

        # Nothing handled it.
        # Now give Drax's conversational brain a chance.
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