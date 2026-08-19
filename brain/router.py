from settings import AI_PROVIDER

from brain.ai import ai


class AIRouter:

    def reason(
        self,
        prompt
    ):

        provider = AI_PROVIDER.lower()

        if provider == "gemini":

            return ai.reason(prompt)

        raise RuntimeError(
            f"Unknown AI provider: {provider}"
        )


router = AIRouter()