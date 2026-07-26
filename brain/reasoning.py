from brain.observation import observation
from brain.session import session_engine
from brain.experience import experience
from brain.companion import companion
from brain.event_bus import bus

class ReasoningEngine:
    
    def __init__(self):

        bus.subscribe(
            "memory_updated",
            self.on_memory_updated
        )

    def on_memory_updated(
        self,
        _
    ):

        self.think()

    def think(self):

        state = observation.observe()

        session = session_engine.detect(
            state
        )

        experience.add(
            session
        )

        print()

        print("🧠 ===== Reasoning =====")

        print(
            session
        )

        print("=======================\n")

        companion.think()


reasoning = ReasoningEngine()