from datetime import datetime
from brain.personality import personality

class PromptBuilder:

    def build(
        self,
        state
    ):

        from datetime import datetime

        now = datetime.now().strftime("%I:%M %p")

        personality_prompt = personality.prompt()

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

    Recent Memory:
    {state['recent_memory']}
    """

        return prompt.strip()


prompt_builder = PromptBuilder()