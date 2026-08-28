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

    IMPORTANT:
    Coordinates returned by Gemini refer to the supplied
    screenshot's coordinate system, NOT necessarily the
    physical Windows screen coordinate system.
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
                "error": f"Screenshot not found: {image_path}",
            }

        instruction = instruction or (
            "Understand this desktop screenshot for Drax, "
            "a computer-use AI agent."
        )

        # --------------------------------------------------------
        # Read the actual screenshot dimensions
        # --------------------------------------------------------

        try:
            with Image.open(path) as image:
                image_width, image_height = image.size

        except Exception as exc:
            return {
                "success": False,
                "error": f"Could not read screenshot: {exc}",
            }

        # --------------------------------------------------------
        # Gemini visual prompt
        # --------------------------------------------------------

        system_prompt = f"""
You are Drax's visual perception system.

Analyze the supplied desktop screenshot.

The screenshot's exact pixel dimensions are:

WIDTH: {image_width}
HEIGHT: {image_height}

COORDINATE SYSTEM:

Return ALL element coordinates using normalized 0-1000 coordinates.

- x = horizontal position from 0 to 1000
- y = vertical position from 0 to 1000
- width = bounding-box width from 0 to 1000
- height = bounding-box height from 0 to 1000
- (0,0) is the top-left
- (1000,1000) is the bottom-right

DO NOT return physical Windows screen coordinates.
DO NOT return screenshot pixel coordinates.
DO NOT assume 1920x1080.

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

Your output MUST be valid JSON.

Use exactly this structure:

{{
  "summary": "short description of the current screen",
  "application": "main visible application",
  "screenshot_size": {{
    "width": {image_width},
    "height": {image_height}
  }},
  "text": [
    "important visible text"
  ],
  "elements": [
    {{
      "label": "visible name",
      "type": "button|input|link|menu|text|image|window|other",
      "x": 0,
      "y": 0,
      "width": 0,
      "height": 0,
      "confidence": 0.0
    }}
  ],
  "possible_actions": [
    "short description of useful actions"
  ]
}}

IMPORTANT:

- x and y are the TOP-LEFT of the bounding box.
- width and height describe the bounding box.
- Do NOT invent UI elements.
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

        # --------------------------------------------------------
        # Send screenshot to Gemini
        # --------------------------------------------------------

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
                "error": "Gemini returned an empty response.",
            }

        # --------------------------------------------------------
        # Parse JSON
        # --------------------------------------------------------

        cleaned = content.strip()

        if cleaned.startswith("```"):
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]

            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]

            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

        try:
            result = json.loads(cleaned)

        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Gemini returned invalid JSON.",
                "raw": content,
            }

        # --------------------------------------------------------
        # Validate / normalize screenshot metadata
        # --------------------------------------------------------

        result["screenshot_size"] = {
            "width": image_width,
            "height": image_height,
        }

        # --------------------------------------------------------
        # Basic coordinate validation
        # --------------------------------------------------------

        elements = result.get("elements", [])

        if isinstance(elements, list):

            valid_elements = []

            for element in elements:

                if not isinstance(element, dict):
                    continue

                try:
                    x = float(element.get("x", 0))
                    y = float(element.get("y", 0))
                    width = float(element.get("width", 0))
                    height = float(element.get("height", 0))

                except (TypeError, ValueError):
                    continue

                # Reject obviously impossible coordinates.
                if x < 0 or y < 0:
                    continue

                if x >= image_width or y >= image_height:
                    continue

                if width < 0 or height < 0:
                    continue

                # Clamp bounding box to screenshot.
                width = min(width, image_width - x)
                height = min(height, image_height - y)

                element["x"] = x
                element["y"] = y
                element["width"] = width
                element["height"] = height

                valid_elements.append(element)

            result["elements"] = valid_elements

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