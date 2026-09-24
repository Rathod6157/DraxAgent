import sys
import json
import traceback
import os
import threading
import time


# ============================================================
# DRAX TAURI BRIDGE
# ============================================================

os.environ["DRAX_BRIDGE"] = "1"
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUNBUFFERED"] = "1"


# ============================================================
# STDOUT / STDERR
# ============================================================
#
# stdout = ONLY JSONL for Tauri
# stderr = Python/debug output
# ============================================================

BRIDGE_STDOUT = sys.stdout

sys.stdout = sys.stderr


# ============================================================
# THREAD-SAFE JSON OUTPUT
# ============================================================

_send_lock = threading.Lock()


def send(message):
    """
    Send exactly one JSON event to Tauri.
    """

    if not isinstance(message, dict):
        return

    try:

        payload = json.dumps(
            message,
            ensure_ascii=False
        )

        with _send_lock:

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
    message_type="assistant"
):

    if text is None:
        return

    text = str(text)

    if not text.strip():
        return

    send({
        "type": "output",
        "message_type": str(message_type),
        "text": text
    })


# ============================================================
# DESKTOP AWARENESS -> TAURI
# ============================================================

def forward_activity_context(data):
    """
    Forward raw foreground-window observations to Tauri.

    Drax's own window is deliberately ignored so the activity
    card continues showing the last real desktop application
    while the user is interacting with Drax.
    """

    if not isinstance(
        data,
        dict
    ):
        return


    application = (
        data.get(
            "application"
        )
        or "Unknown application"
    )


    process = (
        data.get(
            "process"
        )
        or ""
    )


    application_text = str(
        application
    ).strip().lower()


    process_text = str(
        process
    ).strip().lower()


    # ---------------------------------------------------------
    # Ignore Drax itself.
    # ---------------------------------------------------------

    if (
        "drax" in application_text
        or "draxagent" in application_text
        or process_text in {
            "drax-ui.exe",
            "python.exe",
            "python3.exe",
            "python3.11",
            "python3.11.exe",
        }
    ):
        return


    window = (
        data.get(
            "title"
        )
        or data.get(
            "window"
        )
        or ""
    )


    observed_at = (
        data.get(
            "timestamp"
        )
        or data.get(
            "observed_at"
        )
        or time.time()
    )


    send({
        "type": "activity_context",

        "application": str(
            application
        ),

        "process": str(
            process
        ),

        "window": str(
            window
        ),

        "observed_at": observed_at
    })


def forward_activity_update(data):
    """
    Forward the AI-refined activity state.
    """

    if not isinstance(data, dict):
        return

    send({
        "type": "activity_updated",

        "activity": str(
            data.get("activity")
            or "Unknown"
        ),

        "confidence": data.get(
            "confidence"
        ),

        "application": str(
            data.get("application")
            or "Unknown application"
        ),

        "process": str(
            data.get("process")
            or ""
        ),

        "window": str(
            data.get("window")
            or ""
        ),

        "started_at": data.get(
            "started_at"
        ),

        "context": data.get(
            "context"
            or ""
        ),

        "visual_context": data.get(
            "visual_context"
        )
    })


# ============================================================
# DESKTOP AWARENESS INITIALIZATION
# ============================================================

def initialize_awareness():
    """
    Initialize Drax's desktop observer and activity engine.

    IMPORTANT:
    Importing these modules creates their shared singletons
    and event-bus subscriptions.
    """

    from brain import observer

    from brain.event_bus import bus

    # Force ActivityEngine singleton to exist.
    from brain import activity_engine
    _ = activity_engine

    # --------------------------------------------------------
    # Raw foreground window -> Tauri
    # --------------------------------------------------------

    bus.subscribe(
        "window_changed",
        forward_activity_context
    )

    # --------------------------------------------------------
    # AI activity -> Tauri
    # --------------------------------------------------------

    bus.subscribe(
        "activity_updated",
        forward_activity_update
    )

    # --------------------------------------------------------
    # Start observer
    # --------------------------------------------------------

    observer.start()

    print(
        "[Bridge] Desktop observer started.",
        file=sys.stderr
    )


# ============================================================
# PENDING ACTIONS
# ============================================================

pending_action = None


PENDING_STATUSES = {
    "confirmation_required",
    "selection_required",
    "close_confirmation_required",
    "web_fallback_confirmation_required",
}


def handle_pending_action(
    pending,
    user_input
):

    status = pending.get(
        "status"
    )

    if status == "close_confirmation_required":

        from skills.close_app import (
            handle_pending_response
        )

        return handle_pending_response(
            pending,
            user_input
        )

    from skills.open_app import (
        handle_pending_response
    )

    return handle_pending_response(
        pending,
        user_input
    )


# ============================================================
# RESULT -> TAURI
# ============================================================

def forward_result(result):

    if result is None:
        return False

    message = getattr(
        result,
        "message",
        None
    )

    if message:

        message = str(
            message
        ).strip()

        if message:

            send({
                "type": "assistant_message",
                "text": message
            })

            return True

    if isinstance(
        result,
        dict
    ):

        message = result.get(
            "message"
        )

        if message:

            message = str(
                message
            ).strip()

            if message:

                send({
                    "type": "assistant_message",
                    "text": message
                })

                return True

        status = result.get(
            "status"
        )

        if (
            status
            and status not in PENDING_STATUSES
        ):

            send({
                "type": "status_done",
                "text": str(
                    status
                ).replace(
                    "_",
                    " "
                ).capitalize()
            })

            return True

    return False


# ============================================================
# INITIALIZATION
# ============================================================

def initialize_drax():

    from terminal import (
        set_output_callback
    )

    from skills.skill_loader import (
        load_skills
    )

    from resolver import (
        get_cached_applications
    )

    # --------------------------------------------------------
    # Import brain systems FIRST.
    # --------------------------------------------------------

    try:

        from brain import services

    except Exception as error:

        services = None

        print(
            f"[Bridge] Brain services warning: {error}",
            file=sys.stderr
        )

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    load_skills()

    # --------------------------------------------------------
    # Terminal -> Tauri
    # --------------------------------------------------------

    set_output_callback(
        frontend_output
    )

    # --------------------------------------------------------
    # Resolver warm-up
    # --------------------------------------------------------

    try:

        get_cached_applications()

    except Exception as error:

        print(
            f"[Bridge] Resolver warm-up skipped: {error}",
            file=sys.stderr
        )

    # --------------------------------------------------------
    # Desktop awareness
    # --------------------------------------------------------

    initialize_awareness()

    return services


# ============================================================
# COMMAND HANDLER
# ============================================================

def handle_command(text):

    response_sent = False

    try:
        from brain.drax import drax
        from brain.event_bus import bus

        # Let Drax's context system know about the message.
        bus.emit("message", text)

        # Start UI thinking state.
        send({
            "type": "typing",
            "value": True
        })

        send({
            "type": "status",
            "text": "Thinking..."
        })

        # Run the public Drax pipeline.
        response = drax.chat(text)

        # -----------------------------------------------------
        # Direct text response
        # -----------------------------------------------------

        if isinstance(response, str):
            response = response.strip()

            if response:
                send({
                    "type": "assistant_message",
                    "text": response
                })

                response_sent = True

        # -----------------------------------------------------
        # Structured response
        # -----------------------------------------------------

        elif response is not None:
            response_sent = forward_result(response)

        # -----------------------------------------------------
        # Empty / unsupported response
        # -----------------------------------------------------

        if not response_sent:
            print(
                "[Bridge] Drax returned no usable response.",
                file=sys.stderr
            )

            send({
                "type": "assistant_message",
                "text": (
                    "I couldn't complete that response. "
                    "Please try again in a moment."
                )
            })

            response_sent = True

    except Exception as error:
        print(
            f"[Bridge] Command failed: {error}",
            file=sys.stderr
        )

        traceback.print_exc(file=sys.stderr)

        send({
            "type": "error",
            "text": str(error)
        })

    finally:
        # Always stop the thinking animation.
        send({
            "type": "typing",
            "value": False
        })

        # Always release the UI busy state.
        send({
            "type": "command_complete"
        })

# ============================================================
# MAIN LOOP
# ============================================================

def main():

    try:

        initialize_drax()

    except Exception as error:

        send({
            "type": "error",
            "text": (
                "Drax initialization failed: "
                f"{error}"
            )
        })

        traceback.print_exc(
            file=sys.stderr
        )

        return

    send({
        "type": "ready"
    })

    # --------------------------------------------------------
    # JSONL loop
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
                "text": "Invalid bridge message."
            })

            continue

        message_type = message.get(
            "type"
        )

        if message_type == "chat":

            text = str(
                message.get(
                    "text",
                    ""
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