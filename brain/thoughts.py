import random
from brain.event_bus import bus
import time
class ThoughtEngine:

    def __init__(self):

        self.last_thought = None

        self.last_time = 0

        self.cooldown = 20

    def generate(self, state):
        
        now = time.time()

        if now - self.last_time < self.cooldown:
            return None

        activity = state.get(
            "type",
            "Unknown"
        )

        confidence = state.get(
            "confidence",
            0
        )

        duration = state.get(
            "duration",
            0
        )

        thoughts = {
            "Coding": [
                "Looks like you're deep in code.",
                "You're probably building something interesting.",
                "You've been coding for a while now."
            ],

            "Browsing": [
                "Looks like you're researching something.",
                "Doing a little digging on the web?",
                "Seems like you're collecting information."
            ],

            "Music": [
                "Nice choice. Hope the music helps.",
                "Music makes everything better.",
                "Looks like you've got something playing."
            ],

            "Gaming": [
                "Having fun?",
                "Game time, huh?",
                "Hope you're winning 😄"
            ],

            "Unknown": [
                "I'm still figuring out what you're doing."
            ]
        }

        pool = thoughts.get(activity, thoughts["Unknown"])

        thought = random.choice(pool)

        if thought == self.last_thought:
            return None

        self.last_thought = thought
        self.last_time = now

        bus.emit(
            "thought",
            thought
        )

        return thought


thoughts = ThoughtEngine()