import time
from collections import deque
from threading import RLock

from brain.event_bus import bus
from brain.context import context
from brain.activity import activity
from brain.desktop_state import desktop_state
from brain.memory import memory
from brain.activity_history import activity_history
from brain.awareness import Awareness

from brain.resource_context import resource_context
from brain.capability_registry import capabilities

class ContextEngine:
    """
    Centralized situational context for Drax.

    The ContextEngine does NOT replace:
        - Observer
        - Memory
        - ActivityEngine
        - ConversationEngine

    It combines their current state into a single, structured
    context snapshot that higher-level intelligence can consume.

    Layers:

        LIVE
            Current desktop/window/activity.

        SESSION
            Recent user interaction and context transitions.

        RECENT
            Recent desktop/activity history.

        DERIVED
            Lightweight facts inferred from the available state.

    The engine deliberately avoids AI reasoning here.
    AI should consume this context rather than own it.
    """

    def __init__(self):

        self._lock = RLock()

        self._started_at = time.time()

        self._last_user_message = None
        self._last_user_message_at = None

        self._last_context_change = None

        self._session_events = deque(
            maxlen=100
        )

        self._window_visits = {}

        self._active = True

        # -----------------------------------------------------
        # Desktop changes
        # -----------------------------------------------------

        bus.subscribe(
            "window_changed",
            self._on_window_changed
        )

        # -----------------------------------------------------
        # User messages
        # -----------------------------------------------------

        bus.subscribe(
            "message",
            self._on_message
        )

        # -----------------------------------------------------
        # Refined activity
        # -----------------------------------------------------

        bus.subscribe(
            "activity_updated",
            self._on_activity_updated
        )

    # =========================================================
    # EVENT HANDLERS
    # =========================================================

    def _on_window_changed(
        self,
        data
    ):

        if not isinstance(data, dict):
            return

        now = time.time()

        application = (
            data.get("application")
            or "Unknown application"
        )

        process = (
            data.get("process")
            or ""
        )

        title = (
            data.get("title")
            or data.get("window")
            or ""
        )

        event = {
            "type": "window_changed",

            "application": str(
                application
            ),

            "process": str(
                process
            ),

            "window": str(
                title
            ),

            "timestamp": (
                data.get("timestamp")
                or now
            )
        }

        with self._lock:

            self._last_context_change = now

            self._session_events.append(
                event
            )

            # Track how often an application has
            # appeared during this session.
            key = str(
                application
            ).strip().lower()

            if key:

                self._window_visits[key] = (
                    self._window_visits.get(
                        key,
                        0
                    )
                    + 1
                )

    def _on_message(
        self,
        message
    ):

        if message is None:
            return

        message = str(
            message
        ).strip()

        if not message:
            return

        now = time.time()

        with self._lock:

            self._last_user_message = message

            self._last_user_message_at = now

            self._session_events.append(
                {
                    "type": "user_message",
                    "text": message,
                    "timestamp": now
                }
            )

    def _on_activity_updated(
        self,
        data
    ):

        if not isinstance(data, dict):
            return

        now = time.time()

        with self._lock:

            self._session_events.append(
                {
                    "type": "activity_updated",

                    "activity": data.get(
                        "activity"
                    ),

                    "application": data.get(
                        "application"
                    ),

                    "window": data.get(
                        "window"
                    ),

                    "confidence": data.get(
                        "confidence"
                    ),

                    "timestamp": now
                }
            )

    # =========================================================
    # LIVE CONTEXT
    # =========================================================

    def live(
        self
    ):
        """
        Return the current desktop situation.

        This intentionally reads the shared state directly
        rather than depending on the UI.
        """

        application = (
            context.current_application
            or activity.application
            or "Unknown application"
        )

        process = (
            context.current_process
            or activity.process
            or ""
        )

        window = (
            context.current_window
            or (
                activity.windows[-1]
                if activity.windows
                else ""
            )
        )

        activity_name = (
            activity.name
            or "Unknown"
        )

        confidence = (
            activity.confidence
        )

        started_at = (
            activity.started_at
        )

        return {
            "application": application,
            "process": process,
            "window": window,

            "activity": activity_name,
            "activity_confidence": confidence,
            "activity_started_at": started_at,

            "foreground": (
                desktop_state.foreground
            )
        }

    # =========================================================
    # SESSION CONTEXT
    # =========================================================

    def session(
        self,
        limit=20
    ):

        with self._lock:

            events = list(
                self._session_events
            )

            last_message = (
                self._last_user_message
            )

            last_message_at = (
                self._last_user_message_at
            )

        return {
            "started_at": self._started_at,

            "duration": max(
                0,
                time.time()
                - self._started_at
            ),

            "last_user_message": (
                last_message
            ),

            "last_user_message_at": (
                last_message_at
            ),

            "events": events[-limit:]
        }

    # =========================================================
    # RECENT CONTEXT
    # =========================================================

    def recent(
        self,
        memory_limit=10,
        activity_limit=10
    ):

        return {
            "memory": memory.get_recent(
                memory_limit
            ),

            "activity": (
                activity_history
                .recent()
                [-activity_limit:]
            )
        }

    # =========================================================
    # DERIVED CONTEXT
    # =========================================================

    def derived(
        self
    ):

        live = self.live()

        application = str(
            live.get(
                "application"
            )
            or ""
        ).strip().lower()

        process = str(
            live.get(
                "process"
            )
            or ""
        ).strip().lower()

        # ---------------------------------------------
        # Drax foreground detection
        # ---------------------------------------------

        drax_foreground = (
            "drax" in application
            or "draxagent" in application
            or process in {
                "python.exe",
                "python3.exe",
                "python3.11",
                "python3.11.exe"
            }
        )

        # ---------------------------------------------
        # Application frequency
        # ---------------------------------------------

        with self._lock:

            visits = dict(
                self._window_visits
            )

        most_used = sorted(
            visits.items(),
            key=lambda item: item[1],
            reverse=True
        )[:5]

        return {
            "drax_foreground": (
                drax_foreground
            ),

            "most_visited_applications": [
                {
                    "application": name,
                    "visits": count
                }

                for name, count
                in most_used
            ],

            "context_age": (
                max(
                    0,
                    time.time()
                    - (
                        self._last_context_change
                        or self._started_at
                    )
                )
            )
        }

    # =========================================================
    # SNAPSHOT
    # =========================================================

    def snapshot(
        self,
        include_recent=True
    ):
        """
        Build the canonical Drax context object.

        This is the primary API that intelligence systems
        should consume.
        """

        live = self.live()

        snapshot = {
            "timestamp": time.time(),

            "live": live,

            "session": self.session(),

            "recent": self.recent(),

            "derived": self.derived(),

            "resource": resource_context.build(
                application=live.get(
                    "application"
                ),
                process=live.get(
                    "process"
                ),
                window=live.get(
                    "window"
                ),
            ),

            "capabilities": capabilities.describe(),
        }

        if include_recent:

            snapshot["recent"] = (
                self.recent()
            )

        return snapshot

    # =========================================================
    # PROMPT CONTEXT
    # =========================================================

    def prompt_context(
        self,
        message=""
    ):
        """
        Produce a compact context object suitable for an
        AI prompt.

        This is intentionally smaller than snapshot().
        """

        live = self.live()

        session = self.session(
            limit=8
        )

        result = {

            "current_application": live[
                "application"
            ],

            "current_process": live[
                "process"
            ],

            "current_window": live[
                "window"
            ],

            "current_activity": live[
                "activity"
            ],

            "activity_confidence": live[
                "activity_confidence"
            ],

            "activity_started_at": live[
                "activity_started_at"
            ],

            "foreground": live.get(
                "foreground"
            ),

            "last_user_message": session[
                "last_user_message"
            ],

            "recent_events": session[
                "events"
            ],

            "resource": resource_context.build(
                application=live.get(
                    "application"
                ),
                process=live.get(
                    "process"
                ),
                window=live.get(
                    "window"
                ),
            ),

            "capabilities": capabilities.describe(),
        }

        if message:

            result[
                "current_request"
            ] = str(
                message
            ).strip()

        return result


# =============================================================
# SINGLE SHARED INSTANCE
# =============================================================

context_engine = ContextEngine()