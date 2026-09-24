from brain.conversation_manager import conversation_manager
from brain.event_bus import bus
from brain.router import router

from brain.ai.response_parser import response_parser
from brain.ai.chat_prompt import chat_prompt

from brain.context_engine import context_engine
from brain.working_memory import working_memory
from brain.companion_prompt import companion_prompt


class Companion:

    def __init__(self):
        self.last_message = None

    # ---------------------------------------------------------
    # OPERATIONAL FALLBACK
    # ---------------------------------------------------------

    def _fallback_reply(self):
        """
        This is an operational error notice, not a conversational
        response. Normal replies must come from the AI pipeline.
        """

        return (
            "I couldn't generate a response right now. "
            "Please try again."
        )

    # ---------------------------------------------------------
    # CHAT
    # ---------------------------------------------------------

    def chat(self, message, execution=None):

        message = str(message or "").strip()

        # Empty input should not create a fabricated response.
        if not message:
            return ""

        try:
            # Build context from Drax's actual environment.
            context = context_engine.prompt_context(message)

            # Preserve execution evidence for AI response generation.
            context["execution"] = execution

            prompt = chat_prompt.build(
                message,
                context
            )

            # All conversational replies—including greetings—
            # go through the AI provider.
            raw_response = router.reason(prompt)

            if not isinstance(raw_response, str):
                raw_response = str(raw_response or "")

            if not raw_response.strip():
                return self._fallback_reply()

            response = response_parser.parse(raw_response)

            if not response or not response.speak:
                return self._fallback_reply()

            answer = str(response.message or "").strip()

            if not answer:
                return self._fallback_reply()

            # Store only the actual generated response.
            self._remember(
                message,
                answer
            )

            return answer

        except Exception as error:

            print(
                f"[Companion Error] {error}"
            )

            return self._fallback_reply()

    # ---------------------------------------------------------
    # MEMORY
    # ---------------------------------------------------------

    def _remember(
        self,
        user_message,
        drax_message
    ):

        try:
            working_memory.add(
                "User",
                user_message
            )

            working_memory.add(
                "Drax",
                drax_message
            )

        except Exception as error:

            print(
                f"[Memory Warning] {error}"
            )

    # ---------------------------------------------------------
    # PROACTIVE THINKING
    # ---------------------------------------------------------

    def think(self):

        if not conversation_manager.can_talk():
            return

        try:
            context = context_engine.prompt_context("")

            prompt = companion_prompt.build(
                context
            )

            raw_response = router.reason(prompt)

            if not isinstance(raw_response, str):
                raw_response = str(raw_response or "")

            if not raw_response.strip():
                return

            response = response_parser.parse(
                raw_response
            )

            if not response or not response.speak:
                return

            message = str(
                response.message or ""
            ).strip()

            if not message:
                return

            # Avoid repeating the same proactive message.
            if message == self.last_message:
                return

            self.last_message = message

            conversation_manager.spoke()

            bus.emit(
                "ai_response",
                message
            )

        except Exception as error:

            print(
                f"[Companion Think Error] {error}"
            )


companion = Companion()