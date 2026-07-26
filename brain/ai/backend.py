from abc import ABC, abstractmethod


class AIBackend(ABC):

    @abstractmethod
    def reason(
        self,
        prompt: str
    ) -> str:
        """
        Send a prompt to the AI model and
        return its response.
        """
        pass