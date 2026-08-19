from datetime import datetime

from brain.awareness import awareness
from brain.working_memory import working_memory


class ContextBuilder:

    def build(
        self,
        message
    ):

        state = awareness.snapshot()

        return {

            "message": message,

            "time": datetime.now().strftime(
                "%I:%M %p"
            ),

            "awareness": state,

            "working_memory":
                working_memory.recent()

        }


context_builder = ContextBuilder()