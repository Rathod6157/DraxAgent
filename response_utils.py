import re

from brain.router import router


# ============================================================
# Drax Response Understanding
# ============================================================
#
# Converts a natural-language response into one of:
#
#     confirm
#     cancel
#     invalid
#
# Fast obvious responses are handled locally.
# Anything less obvious is understood by Drax's AI layer.
#
# ============================================================


def _normalize(text):
    """
    Light normalization only.

    We deliberately do NOT try to understand language here.
    That is the AI's job.
    """

    if text is None:
        return ""

    text = str(text).strip()

    # Normalize repeated whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


def _fast_classify(text):
    """
    Handle extremely obvious responses without an AI call.

    Returns:
        "confirm"
        "cancel"
        None
    """

    normalized = (
        text
        .lower()
        .strip()
    )

    # Remove harmless surrounding punctuation.
    cleaned = normalized.strip(
        " \t\n\r.,!?;:"
    )

    if not cleaned:
        return None

    # Single-character confirmations.
    if cleaned == "y":
        return "confirm"

    if cleaned == "n":
        return "cancel"

    # Exact common responses.
    if cleaned in {
        "yes",
        "yeah",
        "yep",
        "yup",
        "sure",
        "okay",
        "ok",
    }:
        return "confirm"

    if cleaned in {
        "no",
        "nope",
        "nah",
        "cancel",
        "stop",
        "nevermind",
        "never mind",
    }:
        return "cancel"

    return None


def classify_response(
    user_input,
    context=None
):
    """
    Understand a user's response to a pending question.

    Returns:
        "confirm"
        "cancel"
        "invalid"

    `context` describes what Drax is asking the user about.
    """

    text = _normalize(
        user_input
    )

    if not text:
        return "invalid"

    # --------------------------------------------------------
    # Fast path
    # --------------------------------------------------------

    fast_result = _fast_classify(
        text
    )

    if fast_result:
        return fast_result

    # --------------------------------------------------------
    # AI understanding
    # --------------------------------------------------------

    context = (
        context
        or "a pending Drax operation"
    )

    prompt = f"""
You are Drax's response-understanding system.

Drax has asked the user for confirmation about:

{context}

The user's response is:

"{text}"

Classify the user's response into EXACTLY ONE label:

CONFIRM
CANCEL
INVALID

Meaning:

CONFIRM:
The user clearly agrees, approves, accepts, or tells Drax to proceed.

Examples:
- yes please
- yeah go ahead
- yesss
- absolutely
- do it
- that's fine
- proceed
- go for it
- close it
- sure bro
- yep, do that

CANCEL:
The user clearly refuses, cancels, declines, or tells Drax not to proceed.

Examples:
- no thanks
- nope
- don't do it
- leave it
- never mind
- actually cancel that
- stop
- forget it

INVALID:
The response does not clearly mean yes or no.

Examples:
- what?
- why?
- tell me more
- maybe
- what happens if I say yes?
- which one?
- I don't know

IMPORTANT:
- Understand natural language.
- Ignore capitalization.
- Ignore harmless punctuation.
- Understand typos such as "yess".
- Do not explain your answer.
- Return ONLY:
  CONFIRM
  CANCEL
  or
  INVALID
"""

    try:

        raw_response = router.reason(
            prompt
        )

    except Exception:
        # If AI fails, fail safely.
        return "invalid"

    if raw_response is None:
        return "invalid"

    result = str(
        raw_response
    ).strip().upper()

    # --------------------------------------------------------
    # Strict output validation
    # --------------------------------------------------------

    if "CONFIRM" in result:
        return "confirm"

    if "CANCEL" in result:
        return "cancel"

    return "invalid"