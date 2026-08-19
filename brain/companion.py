from brain.event_bus import bus
from brain.conversation_manager import conversation_manager
from brain.router import router

from brain.ai.prompt_builder import prompt_builder
from brain.ai.response_parser import response_parser
from brain.ai.chat_prompt import chat_prompt

from brain.context_builder import context_builder
from brain.working_memory import working_memory
from brain.companion_prompt import companion_prompt


class Companion:

    def __init__(self):

        self.last_message = None


    def chat(
        self,
        message,
        execution=None
    ):

        context = context_builder.build(
            message
        )

        # Attach execution information to the context.
        context["execution"] = execution

        prompt = chat_prompt.build(
            message,
            context
        )

        raw_response = router.reason(
            prompt
        )

        response = response_parser.parse(
            raw_response
        )

        if not response.speak:

            return


        working_memory.add(
            "User",
            message
        )

        working_memory.add(
            "Drax",
            response.message
        )

        working_memory.debug()

        return response.message


    def think(self):

        if not conversation_manager.can_talk():

            return


        context = context_builder.build(
            ""
        )

        prompt = companion_prompt.build(
            context
        )

        raw_response = router.reason(
            prompt
        )

        response = response_parser.parse(
            raw_response
        )

        if not response.speak:

            return


        if response.message == self.last_message:

            return


        self.last_message = response.message

        conversation_manager.spoke()

        bus.emit(
            "ai_response",
            response.message
        )


companion = Companion()