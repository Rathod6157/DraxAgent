import json
import re


class AutomationPlanner:
    """
    Converts a natural-language task into a structured
    desktop automation plan.

    The planner decides WHAT Drax should do.
    DesktopAutomation decides HOW to execute it.
    """

    def __init__(self, ai_backend=None):
        self.ai_backend = ai_backend

    # ============================================================
    # BUILD PLAN
    # ============================================================

    def build_plan(self, instruction):

        if not instruction or not instruction.strip():
            return {
                "success": False,
                "error": "No automation instruction provided."
            }

        instruction = instruction.strip()

        # --------------------------------------------------------
        # AI planner
        # --------------------------------------------------------

        if self.ai_backend:

            try:
                response = self.ai_backend(instruction)

                plan = self._parse_response(response)

                if plan:
                    return {
                        "success": True,
                        "plan": plan
                    }

            except Exception as error:

                return {
                    "success": False,
                    "error": f"Planner failed: {error}"
                }

        # --------------------------------------------------------
        # Temporary deterministic fallback
        #
        # This lets us test the automation pipeline BEFORE
        # connecting the actual AI brain.
        # --------------------------------------------------------

        return self._fallback_plan(instruction)

    # ============================================================
    # PARSE AI RESPONSE
    # ============================================================

    def _parse_response(self, response):

        if isinstance(response, dict):

            if "actions" in response:
                return response["actions"]

            if "plan" in response:
                return response["plan"]

        if not isinstance(response, str):
            return None

        text = response.strip()

        # Remove markdown code fences if the model adds them.

        text = re.sub(
            r"^```(?:json)?",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"```$",
            "",
            text
        )

        text = text.strip()

        try:

            data = json.loads(text)

        except json.JSONDecodeError:

            return None

        if isinstance(data, list):
            return data

        if isinstance(data, dict):

            actions = data.get("actions")

            if isinstance(actions, list):
                return actions

        return None

    # ============================================================
    # TEMPORARY FALLBACK
    # ============================================================

    def _fallback_plan(self, instruction):

        text = instruction.lower()

        # --------------------------------------------------------
        # YouTube search
        # --------------------------------------------------------

        if "youtube" in text and "search" in text:

            query = self._extract_search_query(
                instruction
            )

            if query:

                return [
                    {
                        "type": "open_url",
                        "url": "https://www.youtube.com"
                    },
                    {
                        "type": "wait",
                        "seconds": 1.2
                    },
                    {
                        "type": "click",
                        "x": 650,
                        "y": 110
                    },
                    {
                        "type": "type",
                        "text": query
                    },
                    {
                        "type": "press",
                        "key": "enter"
                    }
                ]

        return []

    # ============================================================
    # QUERY EXTRACTION
    # ============================================================

    def _extract_search_query(self, instruction):

        patterns = [
            r"search youtube for (.+)",
            r"search youtube (?:for )?(.+)",
            r"youtube search (?:for )?(.+)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                instruction,
                flags=re.IGNORECASE
            )

            if match:

                return match.group(1).strip()

        return None


planner = AutomationPlanner()