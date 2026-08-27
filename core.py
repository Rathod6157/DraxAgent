import re

from models import Task

from config import (
    GREETINGS,
    OPEN_WORDS,
    EXIT_WORDS,
    STOP_WORDS
)

from utils import (
    clean_words,
    fuzzy_match,
    normalize_words,
    tokenize
)

from parser import (
    parse,
    HELP_WORDS,
    TIMER_WORDS,
    TIMER_MANAGEMENT_WORDS
)

from brain.ai.intent_router import intent_router
from open_target_resolver import resolve_open_target


def _split_compound(command: str):

    parts = re.split(
        r"\s*,\s*(?:and\s+)?|\s+\band\b\s+",
        command,
        flags=re.IGNORECASE
    )

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def _understand_single(command: str) -> Task:

    command = command.strip()

    command_lower = command.lower()

    words = tokenize(
        command_lower
    )

    words = normalize_words(
        words
    )

    words = clean_words(
        words,
        STOP_WORDS
    )

    ALL_WORDS = (
        GREETINGS
        + OPEN_WORDS
        + EXIT_WORDS
        + list(HELP_WORDS)
        + list(TIMER_WORDS)
        + list(TIMER_MANAGEMENT_WORDS)
    )

    words = [
        fuzzy_match(
            word,
            ALL_WORDS,
            cutoff=0.72
        )
        if len(word) >= 4
        else word
        for word in words
    ]

    parsed = parse(
        words
    )

    # -----------------------
    # Greeting
    # -----------------------

    if words:

        first = words[0]

        if (
            first in GREETINGS
            and len(words) == 1
        ):

            return Task(
                intent="greeting",
                data={
                    "raw_command": command,
                    "words": words
                }
            )

    # -----------------------
    # Exit
    # -----------------------

    if any(
        word in EXIT_WORDS
        for word in words
    ):

        return Task(
            intent="exit",
            data={
                "raw_command": command,
                "words": words
            }
        )

    # -----------------------
    # Skill
    # -----------------------

    if parsed["action"]:

        target = parsed.get(
            "target"
        )

        if parsed["action"] == "timer":

            target = command

        return Task(
            intent=parsed["action"],
            target=target,
            data={
                "raw_command": command,
                "routing_text": " ".join(words),
                "words": words,
                "target": target
            }
        )

    # -----------------------
    # Conversation
    # -----------------------

    return Task(
        intent="conversation",
        data={
            "raw_command": command,
            "words": words
        }
    )


def understand_with_ai(
    command: str,
    recent_conversation=None
) -> Task:

    plan = intent_router.route(
        command,
        recent_conversation
    )

    actions = plan.get(
        "actions",
        []
    )

    conversation = plan.get(
        "conversation"
    )

    # ---------------------------------
    # Pure conversation
    # ---------------------------------

    if not actions:

        return Task(
            intent="conversation",
            data={
                "raw_command": command,
                "conversation": conversation,
                "ai_plan": plan
            }
        )

    # ---------------------------------
    # Build child action tasks
    # ---------------------------------

    child_tasks = []

    for action in actions:

        child_tasks.append(
            Task(
                intent=action["intent"],
                target=action.get("target"),
                confidence=1.0,
                data={
                    "raw_command": command,

                    "target": action.get(
                        "target"
                    ),

                    "browser": action.get(
                        "browser",
                        "default"
                    ),

                    # IMPORTANT:
                    # Preserve search engine.
                    "engine": action.get(
                        "engine",
                        "google"
                    ),

                    # IMPORTANT:
                    # Preserve website restriction.
                    "site": action.get(
                        "site"
                    ),

                    # Compatibility with older code.
                    "site_domain": action.get(
                        "site"
                    ),

                    "conversation": None
                }
            )
        )

    # ---------------------------------
    # Preserve conversation/question
    # ---------------------------------

    if conversation:

        child_tasks.append(
            Task(
                intent="conversation",
                confidence=1.0,
                data={
                    "raw_command": conversation,
                    "conversation": conversation
                }
            )
        )

    # ---------------------------------
    # One action and NO conversation
    # → normal single task
    # ---------------------------------

    if (
        len(actions) == 1
        and not conversation
    ):

        action = actions[0]

        # ---------------------------------
        # Smart open resolution
        # ---------------------------------

        if action.get("intent") in {
            "open_app",
            "open_web"
        }:

            target = action.get(
                "target"
            )

            open_decision = resolve_open_target(
                target,
                action["intent"]
            )

            # ---------------------------------
            # Strong local application
            # ---------------------------------

            if open_decision["status"] == "app":

                return Task(
                    intent="open_app",
                    target=target,
                    confidence=1.0,
                    data={
                        "raw_command": command,
                        "target": target,
                        "browser": None,
                        "conversation": conversation,
                        "ai_plan": plan,
                        "open_resolution": open_decision
                    }
                )

            # ---------------------------------
            # AI said app, but no local app.
            # Use web.
            # ---------------------------------

            if open_decision["status"] == "web_fallback":

                return Task(
                    intent="open_web",
                    target=target,
                    confidence=1.0,
                    data={
                        "raw_command": command,
                        "target": target,
                        "destination": target,
                        "browser": action.get(
                            "browser",
                            "default"
                        ),
                        "conversation": conversation,
                        "ai_plan": plan,
                        "open_resolution": open_decision
                    }
                )

            # ---------------------------------
            # Website with matching local app.
            # Ask user.
            # ---------------------------------

            if open_decision["status"] == "app_or_web":

                return Task(
                    intent="open_app",
                    target=target,
                    confidence=1.0,
                    data={
                        "raw_command": command,
                        "target": target,
                        "browser": None,
                        "conversation": conversation,
                        "ai_plan": plan,
                        "open_resolution": open_decision,
                        "requires_open_choice": True
                    }
                )

        # ---------------------------------
        # Normal single action
        # ---------------------------------

        # Preserve every field produced by the router.
        # Do not hardcode skill-specific parameters here.

        task_data = dict(action)

        task_data["raw_command"] = command
        task_data["target"] = action.get("target")
        task_data["conversation"] = None
        task_data["ai_plan"] = plan

        return Task(
            intent=action["intent"],
            target=action.get("target"),
            confidence=1.0,
            data={
                "raw_command": command,

                "target": action.get(
                    "target"
                ),

                "browser": action.get(
                    "browser",
                    "default"
                ),

                # IMPORTANT:
                # Preserve search engine.
                "engine": action.get(
                    "engine",
                    "google"
                ),

                # IMPORTANT:
                # Preserve website restriction.
                "site": action.get(
                    "site"
                ),

                # Compatibility.
                "site_domain": action.get(
                    "site"
                ),

                "conversation": None,

                "ai_plan": plan
            }
        )

    # ---------------------------------
    # Multiple actions OR
    # action + conversation
    # → compound
    # ---------------------------------

    return Task(
        intent="compound",
        confidence=1.0,
        data={
            "raw_command": command,
            "tasks": child_tasks,
            "conversation": conversation,
            "ai_plan": plan
        }
    )


def understand(
    command: str
) -> Task:

    command = command.strip()

    if not command:

        return Task(
            intent="conversation",
            data={
                "raw_command": "",
                "words": []
            }
        )

    # -----------------------------------------
    # AI-FIRST UNDERSTANDING
    # -----------------------------------------

    try:

        ai_task = understand_with_ai(
            command
        )

        # If the AI successfully produced
        # an actionable intent, trust it.

        if ai_task.intent not in {
            "conversation"
        }:

            return ai_task

        # AI explicitly classified this as
        # conversation.
        #
        # This is important because we do NOT
        # want the old parser accidentally turning
        # normal conversation into a command.

        if (
            ai_task.data
            and ai_task.data.get(
                "ai_plan"
            )
        ):

            return ai_task

    except Exception as error:

        print(
            f"⚠️ AI understanding failed: {error}"
        )

    # -----------------------------------------
    # LEGACY FALLBACK
    # -----------------------------------------

    return _understand_single(
        command
    )


if __name__ == "__main__":

    tests = [
        "Hey bro, what's up?",
        "I'm tired.",
        "Open Chrome",
        "Open YouTube",
        "Open YouTube in Chrome",
        "Search YouTube for Minecraft tutorials",
        "Search Google for Minecraft tutorials",
        "Search Bing for Python decorators",
        "Search DuckDuckGo for Linux tutorials",
        "Search the web for Minecraft Bedwars",
        "Close Spotify",
        "Set a timer for 10 minutes",
        "Open Chrome and open YouTube",
        "Open YouTube and who is the best Bedwars player?"
    ]

    for test in tests:

        print(
            "\nUSER:",
            test
        )

        task = understand(
            test
        )

        print(
            "INTENT:",
            task.intent
        )

        print(
            "TARGET:",
            task.target
        )

        print(
            "DATA:",
            task.data
        )