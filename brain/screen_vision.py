import json
import os
from pathlib import Path

from google import genai
from PIL import Image


class ScreenVision:
    """
    Gemini-powered visual perception for Drax.

    Takes a desktop screenshot and converts it into
    structured information that Drax can use.
    """

    def __init__(
        self,
        model="gemini-3.5-flash-lite",
        api_key=None,
    ):
        self.model = model

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

    # ============================================================
    # ANALYZE SCREEN
    # ============================================================

    def analyze(
        self,
        image_path,
        instruction=None,
    ):
        """
        Analyze a desktop screenshot with Gemini.
        """

        path = Path(image_path)

        if not path.exists():
            return {
                "success": False,
                "error": f"Screenshot not found: {image_path}"
            }

        instruction = instruction or (
            "Understand this desktop screenshot for Drax, "
            "a computer-use AI agent."
        )

        system_prompt = """
You are Drax's visual perception system.

Analyze the supplied desktop screenshot.

Identify visible:
- applications
- windows
- buttons
- input fields
- links
- menus
- dialogs
- important text
- interactive elements
- approximate screen coordinates

Your output MUST be valid JSON.

Use exactly this structure:

{
  "summary": "short description of the current screen",
  "application": "main visible application",
  "text": [
    "important visible text"
  ],
  "elements": [
    {
      "label": "visible name",
      "type": "button|input|link|menu|text|image|window|other",
      "x": 0,
      "y": 0,
      "width": 0,
      "height": 0,
      "confidence": 0.0
    }
  ],
  "possible_actions": [
    "short description of useful actions"
  ]
}

IMPORTANT:

- Coordinates must refer to the screenshot.
- Do not invent UI elements.
- Only report things actually visible.
- Use lower confidence when uncertain.
- Prefer approximate bounding boxes over random exact coordinates.
- Keep the response concise.
"""

        prompt = (
            system_prompt
            + "\n\n"
            + instruction
            + "\n\nAnalyze the screenshot carefully."
        )

        try:
            image = Image.open(path)

            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    prompt,
                    image,
                ],
            )

        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
            }

        content = getattr(response, "text", None)

        if not content:
            return {
                "success": False,
                "error": "Gemini returned an empty response."
            }

        # ========================================================
        # PARSE JSON
        # ========================================================

        cleaned = content.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.replace(
                "```json", "", 1
            )
            cleaned = cleaned.replace(
                "```", "", 1
            )
            cleaned = cleaned.strip()

        try:
            result = json.loads(cleaned)

        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Gemini returned invalid JSON.",
                "raw": content,
            }

        return {
            "success": True,
            "model": self.model,
            "image": str(path),
            "vision": result,
        }


# ================================================================
# SHARED INSTANCE
# ================================================================

vision = ScreenVision()