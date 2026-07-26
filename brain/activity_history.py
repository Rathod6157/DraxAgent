from collections import deque
import time


class ActivityHistory:

    def __init__(self):

        self.history = deque(
            maxlen=30
        )

    def add(
        self,
        activity
    ):

        self.history.append(
            {
                "activity": activity,
                "time": time.time()
            }
        )

    def recent(self):

        return list(self.history)


activity_history = ActivityHistory()