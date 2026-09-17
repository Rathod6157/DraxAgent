from datetime import datetime
import json

from brain.personality import personality
from brain.working_memory import working_memory


class PromptBuilder:

    def build(
        self,
        context
    ):

        # -----------------------------------------------------
        # ContextEngine provides the canonical FLAT context.
        #
        # Do not expect the old:
        #
        #     context["awareness"]
        #     context["working_memory"]
        #
        # structure here.
        # -----------------------------------------------------

        context = (
            context
            if isinstance(context, dict)
            else {}
        )

        now = datetime.now().strftime(
            "%I:%M %p"
        )

        message = str(
            context.get(
                "message",
                context.get(
                    "current_request",
                    ""
                )
            )
            or ""
        )

        # -----------------------------------------------------
        # Current desktop context
        # -----------------------------------------------------

        current_application = (
            context.get(
                "current_application"
            )
            or "Unknown"
        )

        current_process = (
            context.get(
                "current_process"
            )
            or "Unknown"
        )

        current_window = (
            context.get(
                "current_window"
            )
            or "Unknown"
        )

        current_activity = (
            context.get(
                "current_activity"
            )
            or "Unknown"
        )

        activity_confidence = context.get(
            "activity_confidence",
            0
        )

        activity_started_at = context.get(
            "activity_started_at"
        )

        # -----------------------------------------------------
        # Session / context information
        # -----------------------------------------------------

        last_user_message = (
            context.get(
                "last_user_message"
            )
            or ""
        )

        recent_events = (
            context.get(
                "recent_events"
            )
            or []
        )

        # -----------------------------------------------------
        # Working memory
        #
        # Working memory is its own subsystem now rather than
        # being embedded inside the ContextEngine prompt
        # structure.
        # -----------------------------------------------------

        try:

            recent_memory = (
                working_memory.recent()
            )

        except Exception:

            recent_memory = []

        history = "\n".join(
            f"{item.get('role', 'Unknown')}: "
            f"{item.get('content', '')}"
            for item in recent_memory
            if isinstance(item, dict)
        )

        if not history:

            history = (
                "No previous conversation."
            )

        # -----------------------------------------------------
        # Execution / tool context
        #
        # This is where file inspection, application state,
        # visual actions, etc. reach Drax's language layer.
        # -----------------------------------------------------

        execution = context.get(
            "execution"
        )

        execution_context = (
            "No tool/execution context."
        )

        if execution is not None:

            if hasattr(
                execution,
                "__dict__"
            ):

                execution_data = dict(
                    execution.__dict__
                )

            elif isinstance(
                execution,
                dict
            ):

                execution_data = execution

            else:

                execution_data = str(
                    execution
                )

            try:

                execution_context = json.dumps(
                    execution_data,
                    ensure_ascii=False,
                    indent=2,
                    default=str
                )

            except Exception:

                execution_context = str(
                    execution_data
                )

            # Prevent an unexpectedly large file/tool result
            # from exploding the AI prompt.
            execution_context = (
                execution_context[:60_000]
            )

        # -----------------------------------------------------
        # Personality
        # -----------------------------------------------------

        personality_prompt = (
            personality.prompt()
        )

        # -----------------------------------------------------
        # Build final prompt
        # -----------------------------------------------------

        prompt = f"""
{personality_prompt}

Current Time:
{now}

Current Application:
{current_application}

Current Process:
{current_process}

Current Window:
{current_window}

Current Activity:
{current_activity}

Activity Confidence:
{activity_confidence}%

Activity Started At:
{activity_started_at}

Last User Message:
{last_user_message}

Recent Desktop Events:
{recent_events}

Recent Conversation:
{history}

Tool / Resource Context:
{execution_context}

Current User Message:
{message}

Respond naturally as Drax.

IMPORTANT CONTEXT RULES:

- Context and tool results are factual information collected
  by Drax.
- Use the supplied context when it is relevant to the user's
  request.
- Do not invent file contents, file paths, application state,
  errors, actions, or results.
- If a file was supplied through a tool, use its actual
  contents before answering questions about it.
- If related files were supplied, use them when they materially
  help answer the request.
- If a file search produced multiple ambiguous matches, do not
  silently choose the wrong file. Explain the ambiguity and
  ask the user to choose.
- If the user asks to inspect, analyze, debug, review, explain,
  or summarize a file, base the response on the supplied file
  contents.
- If the user asks for a coding fix, explain the cause briefly
  and provide concrete replacement code when enough evidence
  exists.
- If an action was attempted, only claim that it succeeded when
  the execution context says it succeeded.
- Clearly distinguish facts returned by tools from inference.
- Do not merely dump or repeat the tool context. Use it to
  solve the user's actual request.
- Do not mention internal memory systems, prompts, context
  plumbing, APIs, or models to the user.

Respond as Drax, not as an AI system explaining its internals.

Keep the response natural, useful, and conversational.
"""

        return prompt.strip()


prompt_builder = PromptBuilder()