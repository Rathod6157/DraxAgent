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

    def process(self, message):

        normalized = self._normalize(message)

        # ---------------------------------------------------------
        # PENDING ACTION
        # ---------------------------------------------------------

        if self.pending_action:
            return self._handle_pending_action(message)

        # ---------------------------------------------------------
        # STANDALONE CONFIRMATION
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # STANDALONE CANCELLATION
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # UNDERSTAND REQUEST
        # ---------------------------------------------------------

        task = understand(message)

        # ---------------------------------------------------------
        # EXECUTE REQUEST
        # ---------------------------------------------------------

        result = execute(task)

        # ---------------------------------------------------------
        # STORE PENDING ACTION
        # ---------------------------------------------------------

        if isinstance(result, dict):

            status = result.get("status")

            if status in {
                "confirmation_required",
                "selection_required",
                "close_confirmation_required",
                "web_fallback_confirmation_required",
            }:
                self.pending_action = result
                return result

        # ---------------------------------------------------------
        # COMPOUND COMMAND
        # ---------------------------------------------------------

        if task.intent == "compound":

            result_data = getattr(result, "data", {}) or {}

            action_results = result_data.get(
                "results",
                []
            )

            conversation_tasks = result_data.get(
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
                    "success": getattr(
                        child_result,
                        "success",
                        False
                    ),
                    "message": getattr(
                        child_result,
                        "message",
                        ""
                    ),
                    "data": getattr(
                        child_result,
                        "data",
                        {}
                    ),
                })

            # If the compound request also contains conversation,
            # let Drax explain the completed actions.
            if conversation_tasks:

                conversation_text = " ".join(
                    child.data.get("raw_command", "")
                    for child in conversation_tasks
                )

                return companion.chat(
                    message,
                    execution={
                        "success": getattr(
                            result,
                            "success",
                            False
                        ),
                        "actions": completed_actions,
                        "conversation": conversation_text,
                    }
                )

            # If the compound operation contains a resource
            # that needs an AI explanation, pass the evidence on.
            needs_ai = any(
                isinstance(item.get("result"), object)
                and isinstance(
                    getattr(item.get("result"), "data", None),
                    dict
                )
                and getattr(
                    item.get("result"),
                    "data",
                    {}
                ).get("ai_response")
                for item in action_results
            )

            if needs_ai:
                response = companion.chat(
                    message,
                    execution={
                        "success": getattr(
                            result,
                            "success",
                            False
                        ),
                        "actions": completed_actions,
                    }
                )

                if isinstance(response, str) and response.strip():
                    return response

            return result

        # ---------------------------------------------------------
        # NORMAL REQUEST
        # ---------------------------------------------------------

        if getattr(result, "handled", False):

            result_data = getattr(result, "data", {}) or {}

            # =====================================================
            # IMPORTANT FIX:
            #
            # File/app operations can succeed without generating
            # a user-facing explanation.
            #
            # If the executor marks the result as needing AI,
            # pass the REAL execution evidence to Companion.
            # =====================================================

            if (
                isinstance(result_data, dict)
                and result_data.get("ai_response")
            ):

                response = companion.chat(
                    message,
                    execution=result
                )

                # ---------------------------------------------
                # Gemini produced a useful response
                # ---------------------------------------------

                if isinstance(response, str) and response.strip():
                    return response

                # ---------------------------------------------
                # Safe fallback if AI returns nothing
                # ---------------------------------------------

                file_context = result_data.get(
                    "file_context",
                    {}
                )

                if isinstance(file_context, dict):

                    file_message = file_context.get("message")

                    if file_message:
                        return str(file_message)

                    file_path = file_context.get("path")

                    if file_path:
                        return (
                            "I found and inspected:\n"
                            f"{file_path}\n\n"
                            "However, I couldn't generate "
                            "the full explanation this time."
                        )

                    matches = file_context.get(
                        "matches",
                        []
                    )

                    if matches:
                        paths = [
                            item.get("path", "")
                            for item in matches
                            if isinstance(item, dict)
                            and item.get("path")
                        ]

                        if paths:
                            return (
                                "I found these matching files:\n"
                                + "\n".join(paths)
                            )

                # ---------------------------------------------
                # App status / other tool fallback
                # ---------------------------------------------

                if getattr(result, "message", None):
                    return result.message

                return (
                    "The operation completed, "
                    "but I couldn't generate its explanation."
                )

            # Normal handled operation — preserve existing flow.
            return result

        # ---------------------------------------------------------
        # CONVERSATIONAL FALLBACK
        # ---------------------------------------------------------

        return companion.chat(
            message,
            execution={
                "handled": getattr(result, "handled", False),
                "success": getattr(result, "success", False),
                "message": getattr(result, "message", ""),
                "data": getattr(result, "data", {}),
            }
        )


# ================================================================
# SHARED INSTANCE
# ================================================================

conversation = ConversationEngine()