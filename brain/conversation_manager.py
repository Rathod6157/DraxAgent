import time
from settings import CONVERSATION_COOLDOWN


class ConversationManager:

    def __init__(self):

        self.cooldown = CONVERSATION_COOLDOWN

        self.last_response = 0


    def can_talk(self):

        now = time.time()

        if now - self.last_response < self.cooldown:

            return False

        return True


    def spoke(self):

        self.last_response = time.time()


conversation_manager = ConversationManager()