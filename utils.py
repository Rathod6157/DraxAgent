from difflib import get_close_matches
import string

def clean_words(words, stop_words):
    cleaned = []

    for word in words:
        if word not in stop_words:
            cleaned.append(word)

    return cleaned

import string

def normalize_words(words):

    cleaned = []

    for word in words:

        word = word.strip(string.punctuation)

        if word:
            cleaned.append(word)

    return cleaned

import string

def tokenize(text):
    text = text.lower()

    translator = str.maketrans("", "", string.punctuation)
    text = text.translate(translator)

    return text.split()


def fuzzy_match(word, choices):
    match = get_close_matches(
        word,
        choices,
        n=1,
        cutoff=0.65
    )

    if match:
        return match[0]

    return word