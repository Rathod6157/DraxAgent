import sys
import json
import traceback
import os
import threading


# ============================================================
# DRAX TAURI BRIDGE
# ============================================================
#
# IMPORTANT ARCHITECTURE:
#
# The Tauri bridge must NOT reimplement Drax's orchestration.
#
# The working PyQt GUI calls:
#
#     drax.chat(...)
#
# so the bridge does the same thing.
#
# The bridge is only responsible for:
#
#     Tauri JSONL <-> Drax
#
# plus forwarding the existing desktop-awareness events.
# ============================================================


os.environ["DRAX_BRIDGE"] = "1"
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUNBUFFERED"] = "1"


# Keep stdout exclusively for the Tauri JSONL protocol.
BRIDGE_STDOUT = sys.stdout
sys.stdout = sys.stderr


SEND_LOCK = threading.Lock()


# ============================================================
# JSON OUTPUT
# ============================================================

def send(message):
    """Send exactly one JSON object to Tauri."""

    if not isinstance(message, dict):
        return

    try:
        payload = json.dumps(
            message,
            ensure_ascii=False,
        )

        with SEND_LOCK:
            BRIDGE_STDOUT.write(
                payload + "\n"
            )
            BRIDGE_STDOUT.flush()

    except Exception:
        traceback.print_exc(
            file=sys.stderr
        )


# ============================================================
# TERMINAL -> TAURI
# ============================================================

def frontend_output(
    text,
    message_type="assistant",
):
    """Forward existing Drax terminal output to the Tauri UI."""

    if text is None:
        return

    text = str(text)

    if not text.strip():
        return

    send({
        "type": "output",
        "message_type": str(message_type),
        "text": text,
    })


# ============================================================
# ACTIVITY -> TAURI
# ============================================================

def forward_activity(payload):
    """
    Forward the existing ActivityEngine payload.

    This is the same event that gui.py consumed.
    """

    if not isinstance(payload, dict):
        return

    send({
        "type": "activity_updated",

        "activity": payload.get(
            "activity",
            "Unknown",
        ),

        "confidence": payload.get(
            "confidence",
            0,
        ),

        "application": payload.get(
            "application"
        ),

        "process": payload.get(
            "process"
        ),

        "window": payload.get(
            "window"
        ),

        "started_at": payload.get(
            "started_at"
        ),

        "context": payload.get(
            "context",
            "",
        ),

        "visual_context": payload.get(
            "visual_context"
        ),
    })


# ============================================================
# AUTONOMOUS COMPANION -> TAURI
# ============================================================

def forward_ai_response(message):
    """Forward autonomous Drax companion messages."""

    if message is None:
        return

    text = str(
        message
    ).strip()

    if not text:
        return

    send({
        "type": "assistant_message",
        "text": text,
        "source": "companion",
    })


# ============================================================
# INITIALIZATION
# ============================================================

def initialize_drax():
    """
    Initialize the shared Drax systems once.

    This restores the pieces that gui.py used to initialize:
        - skills
        - resolver cache
        - observer
        - ActivityEngine
        - event subscriptions
        - terminal output callback
    """

    from terminal import set_output_callback
    from skills.skill_loader import load_skills
    from resolver import get_cached_applications

    from brain.event_bus import bus

    # Import these modules so their existing singletons and
    # subscriptions are created inside the bridge process.
    from brain import observer
    from brain import activity_engine  # noqa: F401

    # Load skills before attaching frontend output so startup
    # capability messages remain normal stderr output.
    load_skills()

    # Warm the resolver once.
    get_cached_applications()

    # Route normal Drax terminal/status output to Tauri.
    set_output_callback(
        frontend_output
    )

    # Existing ActivityEngine -> Tauri.
    bus.subscribe(
        "activity_updated",
        forward_activity,
    )

    # Existing autonomous companion -> Tauri.
    bus.subscribe(
        "ai_response",
        forward_ai_response,
    )

    # This is what causes window_changed -> ActivityEngine ->
    # activity_updated to actually happen.
    observer.start()

    return observer


# ============================================================
# RESULT -> TAURI
# ============================================================

def forward_chat_response(response):
    """
    Convert the same response shapes handled by gui.py
    into a Tauri assistant message.

    Returns True when something was forwarded.
    """

    # Direct string response.
    if isinstance(response, str):

        text = response.strip()

        if text:
            send({
                "type": "assistant_message",
                "text": text,
            })

            return True

        return False

    if response is None:
        return False

    # ExecutionResult-style object.
    message = getattr(
        response,
        "message",
        None,
    )

    if message:

        text = str(
            message
        ).strip()

        if text:
            send({
                "type": "assistant_message",
                "text": text,
            })

            return True

    # Dictionary-style response.
    if isinstance(response, dict):

        message = response.get(
            "message"
        )

        if message:

            text = str(
                message
            ).strip()

            if text:
                send({
                    "type": "assistant_message",
                    "text": text,
                })

                return True

        status = response.get(
            "status"
        )

        if status:

            send({
                "type": "status_done",
                "text": str(status).replace(
                    "_",
                    " ",
                ).capitalize(),
            })

            return True

    return False


# ============================================================
# COMMAND HANDLER
# ============================================================

def handle_command(text):
    """
    Send the command through Drax's REAL public chat API.

    Do NOT duplicate core.py + executor.py + companion.py here.

    The PyQt GUI already proved that drax.chat() is the correct
    orchestration boundary.
    """

    try:

        from brain.drax import drax

        send({
            "type": "typing",
            "value": True,
        })

        send({
            "type": "status",
            "text": "Thinking...",
        })

        # ----------------------------------------------------
        # THIS IS THE CRITICAL FIX.
        #
        # Use the exact same high-level entry point as gui.py.
        # ----------------------------------------------------

        response = drax.chat(
            text
        )

        # ----------------------------------------------------
        # Forward the normal chat response.
        # ----------------------------------------------------

        if not forward_chat_response(
            response
        ):

            # Some commands intentionally communicate through
            # terminal/status output or pending-state UI.
            #
            # Do not invent a fake response here.
            print(
                "[Bridge] drax.chat() returned no direct response.",
                file=sys.stderr,
            )

    except Exception as error:

        send({
            "type": "error",
            "text": str(error),
        })

        traceback.print_exc(
            file=sys.stderr
        )

    finally:

        send({
            "type": "typing",
            "value": False,
        })


# ============================================================
# MAIN LOOP
# ============================================================

def main():

    try:

        initialize_drax()

    except Exception as error:

        print(
            f"[Bridge] Initialization failed: {error}",
            file=sys.stderr,
        )

        send({
            "type": "error",
            "text": (
                "Drax bridge initialization failed: "
                f"{error}"
            ),
        })

        return

    # Tell Tauri the backend is ready.
    send({
        "type": "ready"
    })

    # --------------------------------------------------------
    # JSONL command loop
    # --------------------------------------------------------

    for line in sys.stdin:

        line = line.strip()

        if not line:
            continue

        try:

            message = json.loads(
                line
            )

        except json.JSONDecodeError:

            send({
                "type": "error",
                "text": "Invalid bridge message.",
            })

            continue

        message_type = message.get(
            "type"
        )

        if message_type == "chat":

            text = str(
                message.get(
                    "text",
                    "",
                )
            ).strip()

            if text:
                handle_command(
                    text
                )

        elif message_type == "ping":

            send({
                "type": "pong"
            })


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
