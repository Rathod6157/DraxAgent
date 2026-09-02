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
        "visual_observe",
        "visual_click",
        "compound",
    }

    SEARCH_ENGINES = {
        "google",
        "bing",
        "duckduckgo",
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


GENERAL RULES:

1. Normal conversation must ALWAYS be "conversation".

2. Only classify something as an executable intent when
   the user is actually asking Drax to perform an action.

3. Do not invent targets.

4. If the user explicitly refers to a desktop application,
   use open_app.

5. If the user explicitly refers to a website or web destination,
   use open_web.

6. "Open Chrome" means:

   open_app
   target="Chrome"

7. "Open YouTube" means:

   open_web
   target="YouTube"

8. "Open YouTube in Chrome" means:

   open_web
   target="YouTube"
   browser="Chrome"

9. "Open Chrome and open YouTube" means compound.

10. If a sentence contains both conversation/question text
    and an executable request, preserve the executable request.


SEARCH_WEB:


11. Use "search_web" when the user wants to search for:

    - information
    - content
    - pages
    - videos
    - posts
    - repositories
    - articles
    - discussions
    - products
    - anything else searchable on the web


12. Searching and opening are different.

    "Open YouTube"

    ->
    open_web
    target="YouTube"


13. A website and a search engine are DIFFERENT concepts.

    A website is the place the user wants information FROM.

    A search engine is the system used to perform the search.


14. If the user explicitly asks to search a particular website,
    put that website's domain in "site".

    Example:

    "Search Reddit for Minecraft Bedwars"

    ->
    intent="search_web"
    target="Minecraft Bedwars"
    site="reddit.com"
    engine="google"


15. Another example:

    "Search GitHub for Python AI agents"

    ->
    intent="search_web"
    target="Python AI agents"
    site="github.com"
    engine="google"


16. Another example:

    "Search YouTube for Minecraft tutorials"

    ->
    intent="search_web"
    target="Minecraft tutorials"
    site="youtube.com"
    engine="google"


17. Another example:

    "Search Mozilla for Firefox extensions"

    ->
    intent="search_web"
    target="Firefox extensions"
    site="mozilla.org"
    engine="google"


18. IMPORTANT:

    The site field is NOT restricted to a predefined list.

    NEVER assume that only Reddit, GitHub, YouTube, Mozilla,
    Stack Overflow, etc. are valid websites.

    If the user specifies ANY website, infer its real domain
    whenever reasonably possible.


19. Examples of arbitrary websites:

    "Search Medium for Python articles"
    -> site="medium.com"

    "Search Wikipedia for Naruto"
    -> site="wikipedia.org"

    "Search Netflix for Stranger Things"
    -> site="netflix.com"

    "Search example.com for cats"
    -> site="example.com"


20. If the user directly provides a domain or URL,
    preserve that domain.

    Example:

    "Search example.com for Minecraft"

    ->
    site="example.com"
    target="Minecraft"


21. If the user does NOT specify a website,
    site MUST be null.

    Example:

    "Search the web for Minecraft tutorials"

    ->
    site=null
    engine="google"


22. The "target" field MUST contain ONLY the actual
    search query.

    Never include:

    - search
    - find
    - site:
    - website names
    - search-engine names
    - browser names


23. Search engine selection:

    "Google X"
    -> engine="google"

    "Search Google for X"
    -> engine="google"

    "Search Bing for X"
    -> engine="bing"

    "Search DuckDuckGo for X"
    -> engine="duckduckgo"


24. If no general search engine is explicitly requested,
    use:

    engine="google"


25. Do NOT treat a website as a search engine.

    "Search Reddit for X"

    means:

    site="reddit.com"
    engine="google"

    NOT:

    engine="reddit"


26. Browser should be "default" unless the user explicitly
    specifies Chrome, Edge, Firefox, etc.

27. If the user explicitly specifies a browser, preserve it.

28. Do not convert a website search into open_web.

29. Do not invent a website merely because the query mentions
    a company, product, person, or topic.

30. VISUAL COMPUTER-USE:

- visual_observe
- visual_click

Use "visual_observe" when the user wants Drax to look at,
understand, describe, inspect, or analyze the current screen.

Examples:

"What's on my screen?"
"What am I looking at?"
"Look at my screen."
"What's happening on my desktop?"
"Tell me what's open."
"Analyze my screen."

For visual_observe:
- target MUST be null.

Use "visual_click" when the user explicitly asks Drax
to click a visible UI element.

Examples:

"Click the Problems tab."
"Click the Settings button."
"Click the search box."
"Press the login button."

For visual_click:
- target MUST contain ONLY the visible thing to click.
- Do not put words like "click", "press", or "find" in target.

Example:

"Click the Problems tab."

->

{{
  "intent": "visual_click",
  "target": "Problems"
}}

"What's on my screen?"

->

{{
  "intent": "visual_observe",
  "target": null
}}

IMPORTANT:
Visual commands must NOT be classified as normal conversation.

31. Return ONLY valid JSON.


JSON FORMAT:

For one action:

{{
    "type": "single",
    "actions": [
        {{
            "intent": "search_web",
            "target": "Minecraft Bedwars",
            "site": "reddit.com",
            "engine": "google",
            "browser": "default"
        }}
    ],
    "conversation": null
}}


For a general web search:

{{
    "type": "single",
    "actions": [
        {{
            "intent": "search_web",
            "target": "Minecraft tutorials",
            "site": null,
            "engine": "google",
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
            "intent": "search_web",
            "target": "Minecraft tutorials",
            "site": "youtube.com",
            "engine": "google",
            "browser": "Chrome"
        }}
    ],
    "conversation": null
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


    def _infer_search_engine(
        self,
        message,
        current_engine
    ):

        text = message.lower().strip()

        # Explicit general search engines only.
        #
        # Websites such as YouTube, Reddit, GitHub, etc.
        # are NOT search engines here.

        if re.search(
            r"\b(?:search\s+(?:on\s+)?google|google)\b",
            text
        ):
            return "google"

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

        if current_engine in self.SEARCH_ENGINES:
            return current_engine

        return "google"


    def _clean_site(
        self,
        site
    ):

        if not site:
            return None

        site = str(site).strip().lower()

        if not site:
            return None

        # Remove protocol.
        site = re.sub(
            r"^https?://",
            "",
            site
        )

        # Remove path.
        site = site.split("/")[0]

        # Remove www.
        site = site.removeprefix(
            "www."
        )

        return site or None


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

        # Remove markdown code fences.
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

        if not isinstance(
            data,
            dict
        ):

            return self._fallback(
                original_message
            )

        actions = data.get(
            "actions",
            []
        )

        if not isinstance(
            actions,
            list
        ):

            return self._fallback(
                original_message
            )

        validated_actions = []

        for action in actions:

            if not isinstance(
                action,
                dict
            ):
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

                cleaned["browser"] = (
                    action.get("browser")
                    or "default"
                )

            if intent == "search_web":

                engine = (
                    action.get("engine")
                    or "google"
                ).strip().lower()

                engine = self._infer_search_engine(
                    original_message,
                    engine
                )

                cleaned["engine"] = engine

                cleaned["site"] = self._clean_site(
                    action.get("site")
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