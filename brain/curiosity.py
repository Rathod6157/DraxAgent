import time


class Curiosity:

    def __init__(self):

        self.last_message = 0

        self.cooldown = 120

    def should_speak(self):

        return (
            time.time()
            - self.last_message
            > self.cooldown
        )

    def spoke(self):

        self.last_message = time.time()


curiosity = Curiosity()