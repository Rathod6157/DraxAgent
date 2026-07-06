from models import Task
from config import GREETINGS, OPEN_WORDS, EXIT_WORDS, STOP_WORDS
from utils import clean_words, fuzzy_match, normalize_words, tokenize
from skills.skill_loader import get_all_skills
from parser import (
    parse,
    HELP_WORDS,
    TIMER_WORDS,
    TIMER_MANAGEMENT_WORDS
)



def understand(command: str) -> Task:

    command = command.lower().strip()

    words = tokenize(command)
    words = normalize_words(words)
    words = clean_words(words, STOP_WORDS)
    ALL_WORDS = (
        GREETINGS
        + OPEN_WORDS
        + EXIT_WORDS
        + list(HELP_WORDS)
        + list(TIMER_WORDS)
        + list(TIMER_MANAGEMENT_WORDS)
    )

    words = [
        fuzzy_match(word, ALL_WORDS, cutoff=0.72)
        if len(word) >= 4
        else word
        for word in words
    ]

    parsed=parse(words)

    # Greetings
    if words:

        first = words[0]

        if first in GREETINGS and len(words) == 1:
            return Task(
                intent="greeting",
                data={
                    "raw_command": command,
                    "words": words
                }
            )

    # Exit
    if any(word in EXIT_WORDS for word in words):
        return Task(
            intent="exit",
            data={
                "raw_command": command,
                "words": words
            }
        )

            
    if parsed["action"]:

        return Task(
            intent=parsed["action"],
            data={
                "raw_command": command,
                "routing_text": " ".join(words),
                "words": words,
                "target": parsed["target"]
            }
        )

        # Timer commands need the original command text because
        # words like "for", "me", "in", etc. matter for parsing.
        if parsed["action"] == "timer":
            target = command

        return Task(
            intent=parsed["action"],
            data={
                "raw_command": command,
                "words": words,
                "target": target
            }
        )

    return Task(
        intent="unknown",
        data={
            "raw_command": command,                
            "words": words
        }
    )