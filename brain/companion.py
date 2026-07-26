from brain.event_bus import bus
from brain.conversation_manager import conversation_manager
from brain.ai import ai
from brain.ai.prompt_builder import prompt_builder
from brain.ai.response_parser import response_parser
from brain.awareness import awareness

class Companion:

    def __init__(self):

        self.last_message = None


    def think(self):

        if not conversation_manager.can_talk():

            return
        state = awareness.snapshot()

        prompt = prompt_builder.build(
            state
        )

        raw_response = ai.reason(prompt)

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