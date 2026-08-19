from brain.conversation import conversation


class Drax:

    def chat(
        self,
        message
    ):

        return conversation.process(
            message
        )


drax = Drax()