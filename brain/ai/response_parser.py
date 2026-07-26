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

    def parse(
        self,
        response: str
    ) -> AIResponse:

        if not response:

            return AIResponse()

        response = response.strip()

        if response.upper() == "SILENT":

            return AIResponse()

        return AIResponse(

            speak=True,

            message=response
        )


response_parser = ResponseParser()