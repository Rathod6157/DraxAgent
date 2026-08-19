class AIResponse:

    def __init__(
        self,
        speak=False,
        message="",
        confidence=1.0
    ):

        self.speak = speak
        self.message = message
        self.confidence = confidence


class ResponseParser:

    SILENT_VALUES = {
        "",
        "silent",
        "<silent>",
        "[silent]",
        "(silent)",
        "no response",
        "<no response>",
    }


    def parse(
        self,
        response: str
    ) -> AIResponse:

        # ---------------------------------
        # Empty / invalid response
        # ---------------------------------

        if not response:

            return AIResponse(
                speak=False
            )

        response = response.strip()

        if not response:

            return AIResponse(
                speak=False
            )


        # ---------------------------------
        # Normalize for control-word checks
        # ---------------------------------

        normalized = response.lower().strip()

        # Remove common surrounding whitespace
        normalized = " ".join(
            normalized.split()
        )


        # ---------------------------------
        # Silent response
        # ---------------------------------

        if normalized in self.SILENT_VALUES:

            return AIResponse(
                speak=False
            )


        # ---------------------------------
        # Normal response
        # ---------------------------------

        return AIResponse(
            speak=True,
            message=response
        )


response_parser = ResponseParser()