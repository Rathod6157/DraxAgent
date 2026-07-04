from dataclasses import dataclass


@dataclass
class Task:
    intent: str
    target: str | None = None
    confidence: float = 1.0
    data: dict | None = None