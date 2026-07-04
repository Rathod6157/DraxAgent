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

def parse(words):

    return {
        "action": find_action(words),
        "target": find_target(words)
    }