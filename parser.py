ACTION_WORDS = {
    "open": {
        "open",
        "launch",
        "run",
        "start"
    }
}

NEGATION_WORDS = {
    "not",
    "don't",
    "dont",
    "never"
}

def find_action(words):

    for action, triggers in ACTION_WORDS.items():

        for word in words:

            if word in triggers:
                return action

    return None

def find_target(words):

    action = find_action(words)

    if action is None:
        return None

    triggers = ACTION_WORDS[action]

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