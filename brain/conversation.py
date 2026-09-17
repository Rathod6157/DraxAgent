from core import understand
from executor import execute

from brain.execution_result import ExecutionResult
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

    def _normalize(
        self,
        message
    ):

        if message is None:

            return ""

        return str(
            message
        ).strip().lower()


    # =============================================================
    # PENDING ACTION
    # =============================================================

    def _handle_pending_action(
        self,
        message
    ):

        status = self.pending_action.get(
            "status"
        )

        normalized = self._normalize(
            message
        )

        # ---------------------------------------------------------
        # Cancellation
        # ---------------------------------------------------------

        if normalized in self.cancellation_words:

            if status == (
                "close_confirmation_required"
            ):

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
        # ---------------------------------------------------------

        if normalized in self.confirmation_words:

            if status == (
                "close_confirmation_required"
            ):

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
            # If another interaction is required, preserve it.
            # -----------------------------------------------------

            if isinstance(
                result,
                dict
            ):

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
            # Operation completed.
            # -----------------------------------------------------

            self.pending_action = None

            return result


        # ---------------------------------------------------------
        # Other pending responses
        #
        # Examples:
        #
        # 1
        # 2
        # Chrome
        # actually open Edge
        # ---------------------------------------------------------

        if status == (
            "close_confirmation_required"
        ):

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
        # Preserve pending state if required.
        # ---------------------------------------------------------

        if isinstance(
            result,
            dict
        ):

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

            action_results = (
                result.data.get(
                    "results",
                    []
                )
                if isinstance(
                    result,
                    ExecutionResult
                )
                else []
            )

            conversation_tasks = (
                result.data.get(
                    "conversation_tasks",
                    []
                )
                if isinstance(
                    result,
                    ExecutionResult
                )
                else []
            )

            completed_actions = []

            for item in action_results:

                child_task = item.get(
                    "task"
                )

                child_result = item.get(
                    "result"
                )

                if child_task is None:
                    continue

                if not isinstance(
                    child_result,
                    ExecutionResult
                ):
                    continue

                action_data = (
                    child_result.data
                    or {}
                )

                completed_actions.append({
                    "intent": (
                        child_task.intent
                    ),
                    "target": (
                        child_task.target
                    ),
                    "success": (
                        child_result.success
                    ),
                    "message": (
                        child_result.message
                    ),
                    "data": action_data,
                })


            # -----------------------------------------------------
            # Extract conversational component, if any.
            # -----------------------------------------------------

            conversation_text = None

            if conversation_tasks:

                conversation_parts = []

                for child in conversation_tasks:

                    if not child.data:
                        continue

                    raw_command = (
                        child.data.get(
                            "raw_command",
                            ""
                        )
                    )

                    if raw_command:

                        conversation_parts.append(
                            raw_command
                        )

                if conversation_parts:

                    conversation_text = (
                        " ".join(
                            conversation_parts
                        )
                    )


            # -----------------------------------------------------
            # IMPORTANT:
            #
            # A compound command can perform several operations
            # without producing a user-facing sentence.
            #
            # Example:
            #
            # "Find main.ts and inspect it."
            #
            # The executor performs the operations.
            #
            # ConversationEngine collects the evidence.
            #
            # Companion turns that evidence into Drax's response.
            # -----------------------------------------------------

            return companion.chat(
                message,
                execution={
                    "success": (
                        result.success
                        if isinstance(
                            result,
                            ExecutionResult
                        )
                        else False
                    ),
                    "actions": (
                        completed_actions
                    ),
                    "conversation": (
                        conversation_text
                    ),
                }
            )


        # =========================================================
        # NORMAL REQUEST
        # =========================================================

        if (
            isinstance(
                result,
                ExecutionResult
            )
            and result.handled
        ):

            return result


        # =========================================================
        # CONVERSATIONAL FALLBACK
        # =========================================================

        if isinstance(
            result,
            ExecutionResult
        ):

            return companion.chat(
                message,
                execution={
                    "handled": (
                        result.handled
                    ),
                    "success": (
                        result.success
                    ),
                    "message": (
                        result.message
                    ),
                    "data": (
                        result.data
                    )
                }
            )


        # ---------------------------------------------------------
        # Defensive fallback
        # ---------------------------------------------------------

        return companion.chat(
            message
        )


# ================================================================
# SHARED INSTANCE
# ================================================================

conversation = ConversationEngine()