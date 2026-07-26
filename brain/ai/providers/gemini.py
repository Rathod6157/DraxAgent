import os

from dotenv import load_dotenv
from google import genai

from ..backend import AIBackend

from settings import AI_MODEL

load_dotenv()


class GeminiBackend(AIBackend):

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "Gemini API Key not found."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = AI_MODEL


    def reason(
        self,
        prompt: str
    ) -> str:

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text.strip()