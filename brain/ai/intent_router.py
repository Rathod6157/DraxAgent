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
        "search_web",
        "close_app",
        "timer",
        "app_status",
        "compound",
    }

    SEARCH_ENGINES = {
        "google",
        "bing",
        "duckduckgo",
    }

    SEARCH_SITES = {
        "youtube",
        "reddit",
        "github",
        "stackoverflow",
        "wikipedia",
        "amazon",
        "quora",
    }

    BROWSERS = {
        "default",
        "chrome",
        "edge",
        "firefox",
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
- search_web
- close_app
- timer
- app_status
- compound

SEARCH MODEL:

For search_web, distinguish between:

1. engine
   The general search engine.

   Allowed:
   - google
   - bing
   - duckduckgo

2. site
   A specific website the user wants to search.

   Examples:
   - youtube
   - reddit
   - github
   - stackoverflow
   - wikipedia
   - amazon
   - quora

   site may also be null.

3. browser
   The desktop browser in which the search should open.

   Allowed:
   - default
   - chrome
   - edge
   - firefox

IMPORTANT:

A website such as YouTube is NOT a browser.

A website such as YouTube or Reddit is also not
necessarily the general search engine.

Treat it as a search destination/site.

Examples:

"Search YouTube for Minecraft tutorials"

-> search_web
-> target="Minecraft tutorials"
-> site="youtube"
-> engine="google"
-> browser="default"

"Search YouTube for Minecraft tutorials in Chrome"

-> search_web
-> target="Minecraft tutorials"
-> site="youtube"
-> engine="google"
-> browser="chrome"

"Search Reddit for Minecraft Bedwars strategies"

-> search_web
-> target="Minecraft Bedwars strategies"
-> site="reddit"
-> engine="google"
-> browser="default"

"Search GitHub for Python Discord bots"

-> search_web
-> target="Python Discord bots"
-> site="github"
-> engine="google"
-> browser="default"

"Search the web for Minecraft Bedwars strategies"

-> search_web
-> target="Minecraft Bedwars strategies"
-> site=null
-> engine="google"
-> browser="default"

"Google Python decorators"

-> search_web
-> target="Python decorators"
-> site=null
-> engine="google"
-> browser="default"

"Search Bing for Python decorators"

-> search_web
-> target="Python decorators"
-> site=null
-> engine="bing"
-> browser="default"

"Search DuckDuckGo for Python decorators"

-> search_web
-> target="Python decorators"
-> site=null
-> engine="duckduckgo"
-> browser="default"

"Open YouTube"

-> open_web
-> target="YouTube"

"Open Chrome"

-> open_app
-> target="Chrome"

"Open YouTube in Chrome"

-> open_web
-> target="YouTube"
-> browser="chrome"

"Open Chrome and search YouTube for Minecraft tutorials"

-> compound

GENERAL RULES:

1. Normal conversation must ALWAYS be "conversation".

2. A conversational sentence containing words that happen
   to resemble an action must NOT become a skill.

3. Only classify something as an executable intent when
   the user is actually asking Drax to perform an action.

4. When the user explicitly refers to a known desktop
   application, classify it as open_app.

5. When the user explicitly refers to a website or web
   destination, classify it as open_web.

6. If the destination could reasonably refer to either a
   desktop application or website, make the best semantic
   guess based on wording.

7. Do NOT invent targets.

8. Searching and opening are different.

9. For search_web, target MUST contain ONLY the actual
   search query.

10. Remove words such as:
    "search"
    "find"
    "google"
    "youtube"
    "reddit"
    "bing"
    "duckduckgo"
    "on"
    "for"
    from the search target when they are command words.

11. Browser should be "default" unless explicitly specified.

12. If the user explicitly specifies Chrome, Edge, or Firefox,
    preserve that browser.

13. If no site is specified, site MUST be null.

14. If no engine is specified, engine MUST be "google".

15. Preserve both action and conversational content when needed.

16. Return ONLY valid JSON.

JSON format for search:

{{
    "type": "single",
    "actions": [
        {{
            "intent": "search_web",
            "target": "Minecraft tutorials",
            "site": "youtube",
            "engine": "google",
            "browser": "default"
        }}
    ],
    "conversation": null
}}

JSON format for conversation:

{{
    "type": "conversation",
    "actions": [],
    "conversation": "{message}"
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

    def _infer_search_destination(
        self,
        message,
        current_site,
        current_engine
    ):
        """
        Deterministically recover explicit search destinations
        from the user's original message.

        This protects against the LLM accidentally converting
        a site-specific search into a generic Google search.
        """

        text = message.lower().strip()

        site_patterns = {
            "youtube": [
                r"\bsearch\s+(?:on\s+)?youtube\b",
                r"\bsearch\s+youtube\b",
                r"\bon\s+youtube\b",
            ],

            "reddit": [
                r"\bsearch\s+(?:on\s+)?reddit\b",
                r"\bsearch\s+reddit\b",
                r"\bon\s+reddit\b",
            ],

            "github": [
                r"\bsearch\s+(?:on\s+)?github\b",
                r"\bsearch\s+github\b",
                r"\bon\s+github\b",
            ],

            "stackoverflow": [
                r"\bsearch\s+(?:on\s+)?stackoverflow\b",
                r"\bsearch\s+stackoverflow\b",
                r"\bon\s+stackoverflow\b",
            ],

            "wikipedia": [
                r"\bsearch\s+(?:on\s+)?wikipedia\b",
                r"\bsearch\s+wikipedia\b",
                r"\bon\s+wikipedia\b",
            ],

            "amazon": [
                r"\bsearch\s+(?:on\s+)?amazon\b",
                r"\bsearch\s+amazon\b",
                r"\bon\s+amazon\b",
            ],

            "quora": [
                r"\bsearch\s+(?:on\s+)?quora\b",
                r"\bsearch\s+quora\b",
                r"\bon\s+quora\b",
            ],
        }

        for site, patterns in site_patterns.items():

            for pattern in patterns:

                if re.search(pattern, text):
                    return site

        if current_site in self.SEARCH_SITES:
            return current_site

        return None

    def _infer_search_engine(
        self,
        message,
        current_engine
    ):
        """
        Deterministically correct explicit general
        search-engine requests.
        """

        text = message.lower().strip()

        if re.search(
            r"\bsearch\s+(?:on\s+)?bing\s+(?:for\s+)?",
            text
        ):
            return "bing"

        if re.search(
            r"\bsearch\s+(?:on\s+)?duckduckgo\s+(?:for\s+)?",
            text
        ):
            return "duckduckgo"

        if re.search(
            r"\b(?:search\s+(?:on\s+)?google|google)\b",
            text
        ):
            return "google"

        if current_engine in self.SEARCH_ENGINES:
            return current_engine

        return "google"

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

            if intent in {
                "open_web",
                "search_web"
            }:

                browser = (
                    action.get("browser")
                    or "default"
                ).strip().lower()

                if browser not in self.BROWSERS:
                    browser = "default"

                cleaned["browser"] = browser

            if intent == "search_web":

                engine = (
                    action.get("engine")
                    or "google"
                ).strip().lower()

                engine = self._infer_search_engine(
                    original_message,
                    engine
                )

                site = (
                    action.get("site")
                )

                if isinstance(site, str):
                    site = site.strip().lower()

                site = self._infer_search_destination(
                    original_message,
                    site,
                    engine
                )

                cleaned["engine"] = engine
                cleaned["site"] = site

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