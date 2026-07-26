import time


class Context:

    def __init__(self):

        self.current_window = None
        self.previous_window = None

        self.window_started = time.time()

        self.last_activity = time.time()

        self.current_task = None

    def set_window(self, title):

        if title == self.current_window:
            return

        self.previous_window = self.current_window

        self.current_window = title

        self.window_started = time.time()

    @property
    def window_duration(self):

        return int(
            time.time() - self.window_started
        )


context = Context()