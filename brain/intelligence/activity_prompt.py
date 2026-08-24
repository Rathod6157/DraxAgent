def build_activity_prompt(
    context
):

    return f"""
You are DraxAgent's desktop activity intelligence system.

Your job is to determine what the user is ACTUALLY doing
from the available desktop context.

Do NOT classify activity based only on the application.

For example:

Chrome + YouTube video
→ Watching Video

Chrome + Medium article
→ Reading

Chrome + Medium editor
→ Writing

Chrome + Google search
→ Researching

Chrome + Gmail
→ Email

Visual Studio Code + Python file
→ Coding

Visual Studio Code + README
→ Writing Documentation

The same application can represent many different activities.

Use the window title as an important signal, but do not
invent information that is not present.

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
- Confidence must be an integer from 0 to 100.
- If the context is insufficient, use "Unknown".
- No markdown.
- No explanation.
- JSON only.

Desktop context:

Application: {context.get("application") or "Unknown"}
Process: {context.get("process") or "Unknown"}
Executable: {context.get("executable") or "Unknown"}
Window title: {context.get("window_title") or "Unknown"}
"""