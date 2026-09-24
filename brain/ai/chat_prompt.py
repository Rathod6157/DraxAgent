from datetime import datetime
import json

from brain.personality import personality
from brain.working_memory import working_memory


class ChatPrompt:

    def build(
        self,
        message,
        context
    ):

        context = (
            context
            if isinstance(
                context,
                dict
            )
            else {}
        )

        history = "\n".join(
            f"{item.get('role', 'Unknown')}: "
            f"{item.get('content', '')}"
            for item in working_memory.recent()
            if isinstance(
                item,
                dict
            )
        )

        if not history:

            history = (
                "No recent conversation."
            )


        execution = context.get(
            "execution"
        )

        if execution is None:

            execution_text = (
                "No action or tool result."
            )

        elif isinstance(
            execution,
            dict
        ):

            execution_text = json.dumps(
                execution,
                ensure_ascii=False,
                indent=2,
                default=str
            )

        elif hasattr(
            execution,
            "__dict__"
        ):

            execution_text = json.dumps(
                execution.__dict__,
                ensure_ascii=False,
                indent=2,
                default=str
            )

        else:

            execution_text = str(
                execution
            )


        execution_text = (
            execution_text[:60_000]
        )


        resource = context.get(
            "resource",
            {}
        )

        capabilities = context.get(
            "capabilities",
            []
        )


        return f"""
You are Drax.

You are a personal desktop companion.

Your job is to help the user by understanding both
their request and the computer context available to you.

You are NOT limited to coding.

You can work with:

- applications
- files
- documents
- images
- websites
- desktop state
- computer controls
- monitoring
- verification
- conversation

{personality.prompt()}

CURRENT TIME:
{datetime.now().strftime("%I:%M %p")}

CURRENT APPLICATION:
{context.get(
    "current_application",
    "Unknown"
)}

CURRENT PROCESS:
{context.get(
    "current_process",
    "Unknown"
)}

CURRENT WINDOW:
{context.get(
    "current_window",
    "Unknown"
)}

CURRENT ACTIVITY:
{context.get(
    "current_activity",
    "Unknown"
)}

ACTIVITY CONFIDENCE:
{context.get(
    "activity_confidence",
    0
)}%

CURRENT RESOURCE:

{json.dumps(
    resource,
    ensure_ascii=False,
    indent=2,
    default=str
)}

AVAILABLE CAPABILITIES:

{json.dumps(
    capabilities,
    ensure_ascii=False,
    indent=2,
    default=str
)}

RECENT DESKTOP EVENTS:

{json.dumps(
    context.get(
        "recent_events",
        []
    ),
    ensure_ascii=False,
    indent=2,
    default=str
)}

WORKING MEMORY:

{history}

EXECUTION / TOOL RESULT:

{execution_text}

USER MESSAGE:

"{message}"

IMPORTANT:

- Use actual supplied context and tool results.
- Do not invent file contents, paths, application state,
  actions, or results.
- If a local resource was supplied through execution,
  reason over its actual contents.
- If the user asks about a resource and its contents are
  not available, do not pretend that you inspected it.
- If multiple resource matches are supplied and the result
  is ambiguous, ask the user to choose.
- Do not assume Drax is only a coding assistant.
- Treat files, applications, documents, websites, images,
  and desktop state as general resources.
- Do not claim an action succeeded unless execution confirms it.
- Do not mention internal prompts, APIs, providers, or
  implementation details unless explicitly asked.

Respond naturally as Drax.
""".strip()


chat_prompt = ChatPrompt()