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
    },
    "close": {
        "close",
        "quit",
        "terminate"
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

HELP_WORDS = {
    "help",
    "commands",
    "features"
}

TIMER_MANAGEMENT_WORDS = {
    "cancel",
    "stop",
    "list",
    "show"
}

STATUS_WORDS = {
    "running",
    "open"
}

LIST_WORDS = {
    "list",
    "show",
    "display",
    "what"
}

WINDOW_WORDS = {
    "window",
    "windows",
    "app",
    "apps",
    "application",
    "applications"
}

def find_action(words):
    # LIST OPEN WINDOWS / RUNNING APPS
    if (
        any(word in LIST_WORDS for word in words)
        and any(word in WINDOW_WORDS for word in words)
        and any(word in STATUS_WORDS for word in words)
    ):
        return "app_status"
    
    # APPLICATION STATUS QUERIES
    if (
        ("running" in words)
        or (
            "open" in words
            and words
            and words[0] not in ACTION_WORDS["open"]
        )
    ):
        return "app_status"
    
    joined_command = " ".join(words)

    # Help commands must be standalone requests.
    if len(words) == 1 and words[0] in HELP_WORDS:
        return "help"

    if joined_command in {
        "what can you do",
        "show me what you can do",
        "what do",
        "show what do"
    }:
        return "help"

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

    # Application commands
    for action in ("open", "close"):

        for word in words:

            if word in ACTION_WORDS[action]:
                return action

    return None


def find_target(words):

    action = find_action(words)

    if action is None:
        return None
    
    if action == "help":
        return "help"
    
    if action == "app_status":
        if (
            any(word in LIST_WORDS for word in words)
            and any(word in WINDOW_WORDS for word in words)
            and any(word in STATUS_WORDS for word in words)
        ):
            return "__list_running_apps__"
        
        ignored_words = {
            "is",
            "open",
            "running"
        }

        target_words = [
            word
            for word in words
            if word not in ignored_words
        ]

        if not target_words:
            return None

        return " ".join(target_words)

    # Timer skill receives the entire command.
    if action == "timer":
        return " ".join(words)

    # Open/close application target extraction.
    triggers = ACTION_WORDS.get(action)

    if not triggers:
        return None

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