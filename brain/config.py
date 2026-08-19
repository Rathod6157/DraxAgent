from settings import *

class Config:

    @property
    def ai_model(self):
        return AI_MODEL

    @property
    def ai_provider(self):
        return AI_PROVIDER

    @property
    def memory_enabled(self):
        return MEMORY_ENABLED

    @property
    def debug(self):
        return DEBUG

    @property
    def development(self):
        return DEVELOPMENT_MODE


config = Config()