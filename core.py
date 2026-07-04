from models import Task
from config import GREETINGS, OPEN_WORDS, EXIT_WORDS, STOP_WORDS
from utils import clean_words, fuzzy_match, normalize_words, tokenize
from skills.skill_loader import get_all_skills
from parser import parse



def understand(command: str) -> Task:

    command = command.lower().strip()

    words = tokenize(command)
    words = normalize_words(words)
    words = clean_words(words, STOP_WORDS)
    ALL_WORDS = (
    GREETINGS +
    OPEN_WORDS +
    EXIT_WORDS
    )

    words = [fuzzy_match(word, ALL_WORDS) for word in words]
    
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
                "words": words,
                "target": parsed["target"]
            }
        )

    return Task(
        intent="unknown",
        data={
            "raw_command": command,                
            "words": words
        }
    )

