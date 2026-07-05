ACTION_WORDS = {
    "open": {
        "open",
        "launch",
        "run",
        "start"
    },

    "timer": {
        "timer",
        "timers",
        "alert",
        "remind"
    }
}


TIMER_WORDS = {
    "timer",
    "alert",
    "remind"
}


NEGATION_WORDS = {
    "not",
    "don't",
    "dont",
    "never"
}


def find_action(words):

    # Timer management commands
    if (
        ("cancel" in words or "stop" in words)
        and ("timer" in words or "timers" in words)
    ):
        return "timer"

    if (
        ("list" in words or "show" in words)
        and ("timer" in words or "timers" in words)
    ):
        return "timer"

    # Normal timer commands
    if any(word in TIMER_WORDS for word in words):
        return "timer"

    # Application-opening commands
    for word in words:
        if word in ACTION_WORDS["open"]:
            return "open"

    return None


def find_target(words):

    action = find_action(words)

    if action is None:
        return None


    # Timer skill receives the entire command.
    # Duration parsing belongs inside timer.py.

    if action == "timer":
        return " ".join(words)


    # Open Application target extraction.

    triggers = ACTION_WORDS["open"]

    target_words = []
    collecting = False

    for word in words:

        if word in triggers:
            collecting = True
            continue

        if collecting:

            if word in NEGATION_WORDS:
                continue

            target_words.append(word)

    if not target_words:
        return None

    return " ".join(target_words)


def has_negation(words):

    joined_command = " ".join(words)

    negation_phrases = {
        "don't",
        "dont",
        "do not",
        "can't",
        "cant",
        "cannot",
        "never"
    }

    return any(
        phrase in joined_command
        for phrase in negation_phrases
    )


def parse(words):

    action = find_action(words)

    if action and has_negation(words):
        return {
            "action": "cancelled",
            "target": None
        }

    return {
        "action": action,
        "target": find_target(words)
    }