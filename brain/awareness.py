from brain.context import context
from brain.memory import memory
from brain.desktop_state import desktop_state
from brain.experience import experience


class Awareness:

    def snapshot(self):

        return {

            "current_window": context.current_window,

            "recent_memory": memory.get_recent(5),

            "recent_sessions": experience.recent()[-5:],

            "foreground": desktop_state.foreground

        }


awareness = Awareness()