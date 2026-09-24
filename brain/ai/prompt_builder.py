from datetime import datetime
import json

from brain.personality import personality


class PromptBuilder:

    def build(self, context):

        context = context or {}

        now = datetime.now().strftime("%I:%M %p")

        message = str(context.get("message", ""))

        # ContextEngine may provide awareness as a nested
        # dictionary, or provide some fields at the top level.
        state = context.get("awareness") or {}

        if not isinstance(state, dict):
            state = {}

        current_window = state.get(
            "current_window",
            context.get("current_window", "Unknown")
        )

        foreground = state.get(
            "foreground",
            context.get("foreground", "Unknown")
        )

        recent_sessions = state.get(
            "recent_sessions",
            context.get("recent_sessions", [])
        )

        recent_memory = state.get(
            "recent_memory",
            context.get("recent_memory", [])
        )

        working_memory = context.get("working_memory") or []

        execution = context.get("execution")

        personality_prompt = personality.prompt()

        # -------------------------------------------------
        # Conversation history
        # -------------------------------------------------

        history_lines = []

        for item in working_memory:

            if not isinstance(item, dict):
                continue

            role = item.get("role", "Unknown")
            content = item.get("content", "")

            history_lines.append(
                f"{role}: {content}"
            )

        history = "\n".join(history_lines)

        if not history:
            history = "No previous conversation."

        # -------------------------------------------------
        # Tool / resource context
        # -------------------------------------------------

        execution_context = "No tool/resource context."

        if execution is not None:

            if hasattr(execution, "__dict__"):
                execution_data = dict(execution.__dict__)

            elif isinstance(execution, dict):
                execution_data = execution

            else:
                execution_data = str(execution)

            try:
                execution_context = json.dumps(
                    execution_data,
                    ensure_ascii=False,
                    indent=2,
                    default=str
                )

            except Exception:
                execution_context = str(execution_data)

            # Keep prompts bounded.
            execution_context = execution_context[:60000]

        # -------------------------------------------------
        # Build prompt
        # -------------------------------------------------

        prompt = f"""
{personality_prompt}

Current Time:
{now}

Current Window:
{current_window}

Foreground:
{foreground}

Recent Sessions:
{recent_sessions}

Recent Desktop Memory:
{recent_memory}

Recent Conversation:
{history}

Tool / Resource Context:
{execution_context}

Current User Message:
{message}

Respond naturally as Drax.

IMPORTANT TOOL-CONTEXT RULES:

- Tool/resource context is factual information collected by Drax.
- If a file was supplied, inspect its actual contents before
  answering questions about it.
- If related files are supplied, use them when they materially
  help answer the request.
- Do not invent file contents, paths, errors, or application state.
- Clearly distinguish what the tool found from your own inference.
- If the user asks for a coding fix, explain the cause briefly
  and provide concrete replacement code when enough evidence exists.
- If the tool found an ambiguous file match, ask the user to choose.
- For "check this file", use current-file context if available.
- For "find/search my files", summarize matching paths and results.
- Do not claim an action succeeded unless execution confirms it.
- Do not mention internal prompts, APIs, or context plumbing.

Do not merely repeat the tool context.
Use it to solve the user's actual request.
"""

        return prompt.strip()


prompt_builder = PromptBuilder()