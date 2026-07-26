from brain.event_bus import bus
from brain.context import context
from brain.desktop_state import desktop_state

class Memory:

    def __init__(self):

        self.events = []

        bus.subscribe(
            "message",
            self.on_message
        )
        
        bus.subscribe(
            "window_changed",
            self.on_window_changed
        )

    def on_message(
        self,
        message
    ):

        self.events.append(message)

        print(
            "[Memory]",
            message
        )
        
    def on_window_changed(
        self,
        data
    ):

        context.set_window(
            data["title"]
        )
        
        desktop_state.set_foreground(
            data["title"]
        )
        
        desktop_state.debug()

        print(
            f"[Memory] Window: {data['title']}"
        )

        self.events.append(
            {
                "type": "window",
                "title": data["title"],
                "timestamp": data["timestamp"]
            }
        )
        
        bus.emit(
            "memory_updated"
        )
    def get_recent(
        self,
        limit=10
    ):

        return self.events[-limit:]


    def latest(self):

        if not self.events:
            return None

        return self.events[-1]

memory = Memory()
