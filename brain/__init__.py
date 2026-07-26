from .awareness import awareness
from .conversation_manager import conversation_manager
from .event_bus import bus
from .memory import memory
from .observer import observer
from .companion import companion
from .ai import ai
from .service_manager import services
from .decision import decision
from .context import context
from .activity import activity
from .activity_engine import activity_engine
from .desktop_state import desktop_state
from .reasoning import reasoning
from .curiosity import curiosity
from .thoughts import thoughts
from .observation import observation
from .session import session_engine
from .experience import experience

services.register(
    "memory",
    memory
)

services.register(
    "observer",
    observer
)

services.register(
    "companion",
    companion
)

services.register(
    "ai",
    ai
)

services.register(
    "decision",
    decision
)

services.register(
    "activity",
    activity_engine
)

services.register(
    "desktop_state",
    desktop_state
)

services.register(
    "reasoning",
    reasoning
)

services.register(
    "curiosity",
    curiosity
)

services.register(
    "thoughts",
    thoughts
)

services.register(
    "observation",
    observation
)

services.register(
    "session",
    session_engine
)

services.register(
    "experience",
    experience
)

services.register(
    "awareness",
    awareness
)

services.register(
    "conversation_manager",
    conversation_manager
)