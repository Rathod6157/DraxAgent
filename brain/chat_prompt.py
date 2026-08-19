from brain.ai.prompt_builder import prompt_builder


class ChatPrompt:

    def build(
        self,
        context
    ):

        return prompt_builder.build(
            context
        )


chat_prompt = ChatPrompt()