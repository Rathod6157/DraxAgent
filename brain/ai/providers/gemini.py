import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

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

        # One bounded request.
        # Avoid stacking SDK retries on top of app retries.
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=12_000,
                retry_options=types.HttpRetryOptions(
                    attempts=1
                ),
            ),
        )

        self.model = AI_MODEL

    def reason(self, prompt: str) -> str:
        started = time.monotonic()

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=768,
                    temperature=0.4,
                ),
            )

            text = (response.text or "").strip()

            elapsed = time.monotonic() - started

            print(
                f"[Gemini] Request completed in {elapsed:.1f}s"
            )

            return text

        except Exception as error:
            elapsed = time.monotonic() - started

            print(
                f"[Gemini Error] Request failed after "
                f"{elapsed:.1f}s: {error}"
            )

            # Empty string signals the caller to use a fallback.
            return ""