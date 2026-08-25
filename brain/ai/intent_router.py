import json
import re

from brain.router import router


class IntentRouter:

    ALLOWED_INTENTS = {
        "conversation",
        "greeting",
        "exit",
        "help",
        "open_app",
        "open_web",
        "close_app",
        "timer",
        "app_status",
        "compound",
    }

    def route(
        self,
        message,
        recent_conversation=None
    ):

        history = recent_conversation or []

        history_text = "\n".join(
            f"{item['role']}: {item['content']}"
            for item in history[-8:]
        )

        if not history_text:
            history_text = "No previous conversation."

        prompt = f"""
You are DraxAgent's intent router.

Your job is ONLY to understand what the user wants
and return a structured JSON execution plan.

Do NOT answer the user.
Do NOT perform the action.
Do NOT explain anything.

Available intents:

- conversation
- greeting
- exit
- help
- open_app
- open_web
- close_app
- timer
- app_status
- compound

Rules:

1. Normal conversation must ALWAYS be "conversation".

2. A conversational sentence containing words that happen
   to resemble an action must NOT become a skill.

   Example:
   "I'm tired."
   -> conversation

   "Today was a bad day and I feel tired."
   -> conversation

3. Only classify something as an executable intent when
   the user is actually asking Drax to perform an action.

4. When the user explicitly refers to a known desktop
   application, classify it as open_app.

5. When the user explicitly refers to a website or web
   destination, classify it as open_web.

6. If the destination could reasonably refer to either
   a desktop application or a website, make the best
   semantic guess based on the wording.

7. Do NOT assume that every famous website is necessarily
   web-only. Desktop applications can have the same name
   as websites.

8. "Open Chrome" normally means:
   open_app -> Chrome

9. "Open YouTube" normally means:
   open_web -> YouTube

10. "Open YouTube in Chrome" means:
    open_web -> YouTube
    browser -> Chrome

11. Explicit website/web language should also indicate "open_web".

   Examples:

   "Open the YouTube website"
   -> open_web -> YouTube

   "Go to github.com"
   -> open_web -> github.com

   "Open Google in my browser"
   -> open_web -> Google

12. "Open Chrome" means:
   open_app -> Chrome

13. "Open Chrome and open YouTube" means:
   compound containing:
   - open_app -> Chrome
   - open_web -> YouTube

   The application execution layer may fall back to the web
   if YouTube is not installed.

14. If the user asks a question while also requesting an action,
    preserve BOTH parts.

    Example:
    "Open YouTube and who is the best Bedwars player?"
    -> compound
       - open_web -> YouTube
       - conversation/question -> preserved as conversational text

15. Do not invent targets.

16. For web destinations, do not require a URL.
    Natural destinations like YouTube, Google, GitHub, etc.
    are valid.

17. Browser should be "default" unless the user explicitly
    specifies one.

18. Return ONLY valid JSON.

JSON format:

For one action:

{{
    "type": "single",
    "actions": [
        {{
            "intent": "open_web",
            "target": "YouTube",
            "browser": "default"
        }}
    ],
    "conversation": null
}}

For conversation:

{{
    "type": "conversation",
    "actions": [],
    "conversation": "{message}"
}}

For compound:

{{
    "type": "compound",
    "actions": [
        {{
            "intent": "open_app",
            "target": "Chrome"
        }},
        {{
            "intent": "open_web",
            "target": "YouTube",
            "browser": "Chrome"
        }}
    ],
    "conversation": "optional conversational/question part"
}}

Recent conversation:
{history_text}

Current user message:
{message}
"""

        raw = router.reason(
            prompt.strip()
        )

        return self._parse(
            raw,
            message
        )


    def _parse(
        self,
        raw,
        original_message
    ):

        if not raw:

            return self._fallback(
                original_message
            )

        raw = raw.strip()

        # Remove markdown code fences if Gemini
        # decides to be annoying.
        raw = re.sub(
            r"^```(?:json)?\s*",
            "",
            raw,
            flags=re.IGNORECASE
        )

        raw = re.sub(
            r"\s*```$",
            "",
            raw
        )

        try:

            data = json.loads(
                raw
            )

        except json.JSONDecodeError:

            return self._fallback(
                original_message
            )

        if not isinstance(data, dict):

            return self._fallback(
                original_message
            )

        actions = data.get(
            "actions",
            []
        )

        if not isinstance(actions, list):

            return self._fallback(
                original_message
            )

        validated_actions = []

        for action in actions:

            if not isinstance(action, dict):
                continue

            intent = action.get(
                "intent"
            )

            if intent not in self.ALLOWED_INTENTS:
                continue

            if intent in {
                "conversation",
                "compound"
            }:
                continue

            cleaned = {
                "intent": intent,
                "target": action.get(
                    "target"
                )
            }

            if intent == "open_web":

                cleaned["browser"] = (
                    action.get("browser")
                    or "default"
                )

            validated_actions.append(
                cleaned
            )

        conversation = data.get(
            "conversation"
        )

        if not isinstance(
            conversation,
            str
        ):
            conversation = None

        plan_type = data.get(
            "type"
        )

        if len(validated_actions) == 0:

            return {
                "type": "conversation",
                "actions": [],
                "conversation": (
                    conversation
                    or original_message
                )
            }

        if len(validated_actions) == 1:

            return {
                "type": "single",
                "actions": validated_actions,
                "conversation": conversation
            }

        return {
            "type": "compound",
            "actions": validated_actions,
            "conversation": conversation
        }


    def _fallback(
        self,
        message
    ):

        return {
            "type": "conversation",
            "actions": [],
            "conversation": message
        }


intent_router = IntentRouter()