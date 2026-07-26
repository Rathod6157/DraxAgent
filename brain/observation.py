from brain.desktop_state import desktop_state
from brain.context import context


class ObservationEngine:

    def observe(self):

        state = desktop_state.current()

        return {

            "foreground": state["foreground"],

            "background": state["background"],

            "recent": state["recent"],

            "window_duration": context.window_duration

        }


observation = ObservationEngine()