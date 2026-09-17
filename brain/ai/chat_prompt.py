from brain.ai.prompt_builder import prompt_builder


class ChatPrompt:

    def build(
        self,
        message,
        context
    ):

        # -----------------------------------------------------
        # ContextEngine now provides the canonical flat
        # context structure.
        #
        # ChatPrompt is only the compatibility layer between
        # Companion and PromptBuilder.
        # -----------------------------------------------------

        prompt_context = dict(
            context
        )

        prompt_context["message"] = (
            message
        )

        return prompt_builder.build(
            prompt_context
        )


chat_prompt = ChatPrompt()