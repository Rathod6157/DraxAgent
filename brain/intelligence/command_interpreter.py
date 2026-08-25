import json

from brain.router import router


class CommandInterpreter:

    SYSTEM_PROMPT = """
You are DraxAgent's command interpreter.

Your job is to understand a user's command and classify ONLY
whether it is a desktop action or a web-opening request.

Return ONLY valid JSON.

Schema:

{
    "action": "open_web" | "none",
    "destination": "",
    "browser": "default" | "",
    "confidence": 0.0
}

Rules:

1. Use "open_web" when the user clearly wants to open a website,
   webpage, web service, URL, search result, or online destination.

2. Extract the destination naturally.
   Examples:
   "open YouTube" -> destination "YouTube"
   "open Gmail" -> destination "Gmail"
   "open github.com" -> destination "github.com"

3. If the user explicitly specifies a browser:
   "open YouTube in Chrome"
   -> browser "Chrome"

4. If no browser is specified:
   -> browser "default"

5. Normal conversation is NOT an action.
   "I watched YouTube today"
   -> none

6. Do not invent actions.

7. Confidence must be between 0 and 1.

Return JSON only. No markdown. No explanation.
"""


    def interpret(self, message):

        prompt = (
            self.SYSTEM_PROMPT
            + "\n\nUser command:\n"
            + message
        )

        raw = router.reason(prompt)

        if not raw:
            return None

        try:

            # Gemini occasionally wraps JSON in ```json ... ```
            raw = raw.strip()

            if raw.startswith("```"):

                raw = raw.replace(
                    "```json",
                    "",
                    1
                )

                raw = raw.replace(
                    "```",
                    "",
                    1
                )

                raw = raw.strip()

            result = json.loads(raw)

            if not isinstance(result, dict):
                return None

            if result.get("action") != "open_web":
                return None

            destination = (
                result.get("destination")
                or ""
            ).strip()

            if not destination:
                return None

            return {
                "action": "open_web",
                "destination": destination,
                "browser": (
                    result.get("browser")
                    or "default"
                ),
                "confidence": float(
                    result.get(
                        "confidence",
                        0
                    )
                )
            }

        except (
            ValueError,
            TypeError,
            json.JSONDecodeError
        ):

            print(
                "[CommandInterpreter] "
                "Invalid AI response."
            )

            return None


command_interpreter = CommandInterpreter()