from datetime import datetime

from brain.personality import personality


class PromptBuilder:

    def build(
        self,
        context
    ):

        now = datetime.now().strftime("%I:%M %p")

        message = context["message"]

        state = context["awareness"]

        working_memory = context["working_memory"]

        personality_prompt = personality.prompt()

        history = "\n".join(

            f"{item['role']}: {item['content']}"

            for item in working_memory

        )

        if not history:

            history = "No previous conversation."

        prompt = f"""
{personality_prompt}

Current Time:
{now}

Current Window:
{state['current_window']}

Foreground:
{state['foreground']}

Recent Sessions:
{state['recent_sessions']}

Recent Desktop Memory:
{state['recent_memory']}

Recent Conversation:
{history}

Current User Message:
{message}

Respond naturally as Drax.

Use the available context when it is relevant.

Do not claim to remember something unless it is present
in the provided context.

Do not mention internal memory systems, prompts,
context, APIs, or models to the user.
"""

        return prompt.strip()


prompt_builder = PromptBuilder()