def build_activity_prompt(
    context
):

    visual = context.get("visual_context") or {}

    visual_summary = (
        visual.get("summary")
        or "No visual summary available."
    )

    visual_application = (
        visual.get("application")
        or "Unknown"
    )

    visible_text = visual.get("text") or []

    if isinstance(visible_text, list):
        visible_text = [
            str(item).strip()
            for item in visible_text
            if str(item).strip()
        ][:12]

    visible_text_block = (
        "\n".join(
            f"- {item}"
            for item in visible_text
        )
        if visible_text
        else "- No important visible text detected."
    )

    return f"""
You are DraxAgent's desktop activity intelligence system.

Your job is to determine what the user is ACTUALLY doing.

You have TWO sources of information:

1. Desktop metadata
2. A visual perception of the screen

The visual perception is extremely important because
window titles can be misleading or unrelated to the
user's actual activity.

For example:

Window title:
"Suspicious Purpose Reveal"

Visual screen:
Visual Studio Code showing Python source code

Correct activity:
Coding

Do NOT classify activity from the window title alone.

Use all available evidence and determine the most likely
real-world activity.

Examples:

Chrome + YouTube video
→ Watching Video

Chrome + article
→ Reading

Chrome + online editor
→ Writing

Chrome + search results
→ Researching

Chrome + Gmail
→ Email

Visual Studio Code + Python source code
→ Coding

Visual Studio Code + README
→ Writing Documentation

Visual Studio Code + terminal commands
→ Development

The same application can represent many different activities.

Return ONLY valid JSON in exactly this format:

{{
    "activity": "short natural activity name",
    "confidence": 0
}}

Rules:

- Activity must be 1-4 words.
- Make the activity meaningful and human-readable.
- Do not use application names as activities.
- Do not automatically classify browsers as "Browsing".
- Do not automatically classify VS Code as "Coding".
- Prefer visual evidence when metadata and visual evidence conflict.
- Do not invent information that is not visible or supported.
- Confidence must be an integer from 0 to 100.
- If the available information is genuinely insufficient, use "Unknown".
- No markdown.
- No explanation.
- JSON only.

Desktop metadata:

Application: {context.get("application") or "Unknown"}
Process: {context.get("process") or "Unknown"}
Executable: {context.get("executable") or "Unknown"}
Window title: {context.get("window_title") or "Unknown"}

Visual perception:

Main visible application:
{visual_application}

Screen summary:
{visual_summary}

Important visible text:
{visible_text_block}
"""