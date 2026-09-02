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

        # ---------------------------------------------------------
        # Natural confirmation / cancellation words
        # ---------------------------------------------------------

        self.confirmation_words = {
            "yes",
            "yeah",
            "yep",
            "yup",
            "sure",
            "okay",
            "ok",
            "affirmative",
            "continue",
            "do it",
            "go ahead",
            "proceed",
        }

        self.cancellation_words = {
            "no",
            "nope",
            "nah",
            "cancel",
            "stop",
            "never mind",
            "nevermind",
        }


    # =============================================================
    # NORMALIZE MESSAGE
    # =============================================================

    def _normalize(self, message):

        if message is None:
            return ""

        return str(message).strip().lower()


    # =============================================================
    # PENDING ACTION
    # =============================================================

    def _handle_pending_action(self, message):

        status = self.pending_action.get(
            "status"
        )

        normalized = self._normalize(
            message
        )

        # ---------------------------------------------------------
        # Cancellation
        #
        # Let the actual skill handler process cancellation so
        # existing skill-specific behaviour remains intact.
        # ---------------------------------------------------------

        if normalized in self.cancellation_words:

            if status == "close_confirmation_required":

                result = handle_close_pending(
                    self.pending_action,
                    message
                )

            else:

                result = handle_open_pending(
                    self.pending_action,
                    message
                )

            self.pending_action = None

            return result


        # ---------------------------------------------------------
        # Confirmation
        #
        # IMPORTANT:
        #
        # Do NOT send "yes" through understand().
        #
        # It belongs to the pending operation.
        # ---------------------------------------------------------

        if normalized in self.confirmation_words:

            if status == "close_confirmation_required":

                result = handle_close_pending(
                    self.pending_action,
                    message
                )

            else:

                result = handle_open_pending(
                    self.pending_action,
                    message
                )

            # -----------------------------------------------------
            # If the skill created another pending operation,
            # preserve it.
            # -----------------------------------------------------

            if isinstance(result, dict):

                next_status = result.get(
                    "status"
                )

                if next_status in {
                    "confirmation_required",
                    "selection_required",
                    "close_confirmation_required",
                }:

                    self.pending_action = result

                    return result

            # -----------------------------------------------------
            # Operation finished.
            #
            # Clear pending state AND return the actual result.
            # -----------------------------------------------------

            self.pending_action = None

            return result


        # ---------------------------------------------------------
        # Other responses
        #
        # Examples:
        #
        # "1"
        # "2"
        # "Chrome"
        # "actually open Edge"
        #
        # These must still go through the skill's pending handler.
        # ---------------------------------------------------------

        if status == "close_confirmation_required":

            result = handle_close_pending(
                self.pending_action,
                message
            )

        else:

            result = handle_open_pending(
                self.pending_action,
                message
            )


        # ---------------------------------------------------------
        # Keep pending state if another interaction is required.
        # ---------------------------------------------------------

        if isinstance(result, dict):

            next_status = result.get(
                "status"
            )

            if next_status in {
                "confirmation_required",
                "selection_required",
                "close_confirmation_required",
            }:

                self.pending_action = result

                return result


        # ---------------------------------------------------------
        # Pending operation completed.
        # ---------------------------------------------------------

        self.pending_action = None

        return result


    # =============================================================
    # PROCESS
    # =============================================================

    def process(
        self,
        message
    ):

        normalized = self._normalize(
            message
        )


        # =========================================================
        # PENDING ACTION
        # =========================================================

        if self.pending_action:

            return self._handle_pending_action(
                message
            )


        # =========================================================
        # STANDALONE CONFIRMATION
        # =========================================================
        #
        # If the user says "yes" without a pending action,
        # DON'T accidentally turn it into a generic successful
        # command.
        #
        # Let Drax respond conversationally instead.
        # =========================================================

        if normalized in self.confirmation_words:

            return companion.chat(
                message,
                execution={
                    "handled": False,
                    "success": False,
                    "message": (
                        "There isn't a pending action "
                        "for me to continue."
                    ),
                    "data": {}
                }
            )


        # =========================================================
        # STANDALONE CANCELLATION
        # =========================================================

        if normalized in self.cancellation_words:

            return companion.chat(
                message,
                execution={
                    "handled": False,
                    "success": False,
                    "message": (
                        "There isn't anything pending "
                        "to cancel."
                    ),
                    "data": {}
                }
            )


        # =========================================================
        # UNDERSTAND REQUEST
        # =========================================================

        task = understand(
            message
        )


        # =========================================================
        # EXECUTE
        # =========================================================

        result = execute(
            task
        )


        # =========================================================
        # STORE PENDING ACTION
        # =========================================================

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
                "close_confirmation_required",
            }:

                self.pending_action = result

                return result


        # =========================================================
        # COMPOUND COMMAND
        # =========================================================

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


        # =========================================================
        # NORMAL REQUEST
        # =========================================================

        if result.handled:

            return result


        # =========================================================
        # CONVERSATIONAL FALLBACK
        # =========================================================

        return companion.chat(
            message,
            execution={
                "handled": result.handled,
                "success": result.success,
                "message": result.message,
                "data": result.data
            }
        )


# ================================================================
# SHARED INSTANCE
# ================================================================

conversation = ConversationEngine()