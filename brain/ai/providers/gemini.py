import os
import time
import threading

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

        self.lock = threading.Lock()

        self.max_retries = 3


    def reason(
        self,
        prompt: str
    ) -> str:

        with self.lock:

            delays = [2, 4, 8]

            for attempt in range(
                self.max_retries
            ):

                try:

                    response = (
                        self.client.models.generate_content(
                            model=self.model,
                            contents=prompt
                        )
                    )

                    if not response.text:

                        return ""

                    return response.text.strip()


                except Exception as error:

                    error_text = str(error)

                    retryable = (
                        "503" in error_text
                        or "UNAVAILABLE" in error_text
                        or "429" in error_text
                        or "RESOURCE_EXHAUSTED" in error_text
                    )

                    if not retryable:

                        print(
                            f"[Gemini Error] {error}"
                        )

                        return ""


                    if attempt >= self.max_retries - 1:

                        print(
                            "[Gemini] Service unavailable "
                            "after retries."
                        )

                        return ""


                    delay = delays[attempt]

                    print(
                        f"[Gemini] Temporary failure. "
                        f"Retrying in {delay}s..."
                    )

                    time.sleep(delay)


        return ""