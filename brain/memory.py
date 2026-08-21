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

        self.events.append(
            message
        )

        print(
            "[Memory]",
            message
        )


    def on_window_changed(
        self,
        data
    ):

        # ---------------------------------
        # Window information
        # ---------------------------------

        title = data.get(
            "title",
            ""
        )

        process = data.get(
            "process"
        )

        executable = data.get(
            "executable"
        )

        pid = data.get(
            "pid"
        )

        timestamp = data.get(
            "timestamp"
        )


        # ---------------------------------
        # Update Context
        # ---------------------------------

        context.set_window(
            title,
            hwnd=data.get("hwnd"),
            application=data.get("application"),
            process=process,
            executable=executable,
            pid=pid
        )


        # ---------------------------------
        # Update Desktop State
        # ---------------------------------

        desktop_state.set_foreground(
            {
                "title": title,
                "application": data.get(
                    "application",
                    "Unknown"
                ),
                "process": process,
                "executable": executable,
                "pid": pid,
                "timestamp": timestamp
            }
        )


        # ---------------------------------
        # Debug
        # ---------------------------------

        desktop_state.debug()

        print(
            f"[Memory] Window: {title}"
        )

        print(
            f"[Memory] Process: {process}"
        )


        # ---------------------------------
        # Store event
        # ---------------------------------

        self.events.append(
            {
                "type": "window",

                "title": title,
                
                "application": context.current_application,

                "process": process,

                "executable": executable,

                "pid": pid,

                "timestamp": timestamp
            }
        )


        # ---------------------------------
        # Notify brain
        # ---------------------------------

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