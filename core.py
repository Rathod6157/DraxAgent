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

    words = tokenize(command_lower)

    words = normalize_words(words)

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

    parsed = parse(words)

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

        target = parsed.get("target")

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


def understand(command: str) -> Task:

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
    # Try compound command
    # -----------------------------------------

    parts = _split_compound(command)

    if len(parts) <= 1:

        return _understand_single(
            command
        )

    tasks = [
        _understand_single(part)
        for part in parts
    ]

    # -----------------------------------------
    # Only call something "compound" if it
    # actually contains an executable action.
    # -----------------------------------------

    actionable_tasks = [
        task
        for task in tasks
        if task.intent not in (
            "conversation",
            "greeting"
        )
    ]

    if not actionable_tasks:

        # It was probably just normal
        # conversational language containing "and".
        return _understand_single(
            command
        )

    return Task(
        intent="compound",
        confidence=min(
            task.confidence
            for task in tasks
        ),
        data={
            "raw_command": command,
            "parts": parts,
            "tasks": tasks
        }
    )