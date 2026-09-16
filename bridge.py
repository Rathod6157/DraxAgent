import sys
import json
import traceback
import os
import threading


# ============================================================
# DRAX TAURI BRIDGE
# ============================================================
#
# stdout = JSONL protocol ONLY
# stderr = Python/debug output
#
# The bridge keeps Drax alive and processes one command at a
# time, while also forwarding desktop-awareness events to Tauri.
# ============================================================


os.environ["DRAX_BRIDGE"] = "1"
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUNBUFFERED"] = "1"


# ============================================================
# BRIDGE STDOUT
# ============================================================

BRIDGE_STDOUT = sys.stdout


# ============================================================
# THREAD-SAFE JSON OUTPUT
# ============================================================
#
# Observer/activity callbacks run outside the command thread.
# Multiple threads must never write JSONL simultaneously.
# ============================================================

_send_lock = threading.Lock()


def send(message):
    """
    Send exactly one JSON event to the Tauri frontend.
    """

    if not isinstance(message, dict):
        return

    with _send_lock:

        BRIDGE_STDOUT.write(
            json.dumps(
                message,
                ensure_ascii=False
            )
            + "\n"
        )

        BRIDGE_STDOUT.flush()


# ============================================================
# PYTHON -> TAURI OUTPUT CALLBACK
# ============================================================

def frontend_output(
    text,
    message_type="assistant"
):
    """
    Forward Drax terminal output into the Tauri frontend.
    """

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
    Forward the observer's immediate foreground-window context
    to the Tauri frontend.

    This is deliberately lightweight.

    It does NOT run AI classification.
    """

    if not isinstance(data, dict):
        return

    application = (
        data.get("application")
        or "Unknown application"
    )

    window_title = (
        data.get("title")
        or data.get("window")
        or ""
    )

    observed_at = data.get(
        "observed_at"
    )

    send({
        "type": "activity_context",
        "application": str(application),
        "process": str(
            data.get("process")
            or ""
        ),
        "window": str(window_title),
        "observed_at": observed_at
    })


def forward_activity_update(data):
    """
    Forward the AI-refined activity state to Tauri.

    ActivityEngine owns the actual intelligence.
    The bridge only transports the result.
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
    Start Drax's desktop observer and connect its event bus
    to the Tauri JSONL bridge.

    This is the important piece that makes the Tauri UI
    actually aware of the desktop.
    """

    from brain import (
        observer,
        bus,
    )

    # --------------------------------------------------------
    # Forward raw foreground-window changes immediately.
    #
    # This gives the UI an instant "Using Chrome" / "Using VS
    # Code" style update before AI classification finishes.
    # --------------------------------------------------------

    bus.subscribe(
        "window_changed",
        forward_activity_context
    )

    # --------------------------------------------------------
    # Forward AI-refined activity.
    #
    # ActivityEngine already produces this event.
    # --------------------------------------------------------

    bus.subscribe(
        "activity_updated",
        forward_activity_update
    )

    # --------------------------------------------------------
    # Start the actual Windows observer.
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
    """
    Route pending confirmations/selections through the same
    handlers used by the normal Drax terminal interface.
    """

    status = pending.get(
        "status"
    )

    # --------------------------------------------------------
    # CLOSE APP
    # --------------------------------------------------------

    if status == "close_confirmation_required":

        from skills.close_app import (
            handle_pending_response
        )

        return handle_pending_response(
            pending,
            user_input
        )


    # --------------------------------------------------------
    # OPEN APP
    # --------------------------------------------------------

    from skills.open_app import (
        handle_pending_response
    )

    return handle_pending_response(
        pending,
        user_input
    )


# ============================================================
# RESULT -> FRONTEND
# ============================================================

def forward_result(result):
    """
    Forward a structured execution result when the terminal
    callback did not already provide the user-facing message.

    Returns True when something was sent.
    """

    if result is None:
        return False


    # --------------------------------------------------------
    # ExecutionResult-style object
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Dictionary-style result
    # --------------------------------------------------------

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
    """
    Initialize bridge dependencies exactly once.
    """

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
    # Import brain services.
    #
    # This loads the shared event bus, ActivityEngine,
    # context, memory, observer, etc.
    # --------------------------------------------------------

    try:

        from brain import services

    except Exception:

        services = None


    # --------------------------------------------------------
    # Load skills ONCE.
    #
    # IMPORTANT:
    # This happens BEFORE installing frontend_output.
    # Therefore startup skill messages stay out of chat.
    # --------------------------------------------------------

    load_skills()


    # --------------------------------------------------------
    # Connect terminal output.
    # --------------------------------------------------------

    set_output_callback(
        frontend_output
    )


    # --------------------------------------------------------
    # Warm application resolver ONCE.
    # --------------------------------------------------------

    try:

        get_cached_applications()

    except Exception:

        pass


    # --------------------------------------------------------
    # START DESKTOP AWARENESS
    # --------------------------------------------------------

    try:

        initialize_awareness()

    except Exception as error:

        print(
            f"[Bridge] Desktop awareness failed: {error}",
            file=sys.stderr
        )

        traceback.print_exc(
            file=sys.stderr
        )


    return services


# ============================================================
# COMMAND HANDLER
# ============================================================

def handle_command(text):

    global pending_action

    response_sent = False

    original_stdout = sys.stdout


    try:

        # ----------------------------------------------------
        # Keep stdout exclusively for JSONL.
        # ----------------------------------------------------

        sys.stdout = sys.stderr


        # ----------------------------------------------------
        # REAL DRAX PIPELINE
        # ----------------------------------------------------

        from core import (
            understand
        )

        from executor import (
            execute
        )

        from brain.companion import (
            companion
        )

        from terminal import (
            set_output_callback
        )


        set_output_callback(
            frontend_output
        )


        # ----------------------------------------------------
        # COMMAND START
        # ----------------------------------------------------

        send({
            "type": "typing",
            "value": True
        })

        send({
            "type": "status",
            "text": "Thinking..."
        })


        # ----------------------------------------------------
        # PENDING ACTION
        # ----------------------------------------------------

        if pending_action is not None:

            pending_action = (
                handle_pending_action(
                    pending_action,
                    text
                )
            )

            return


        # ----------------------------------------------------
        # UNDERSTAND
        # ----------------------------------------------------

        task = understand(
            text
        )


        # ----------------------------------------------------
        # EXECUTE
        # ----------------------------------------------------

        result = execute(
            task
        )


        # ----------------------------------------------------
        # STORE PENDING OPERATION
        # ----------------------------------------------------

        if (
            isinstance(
                result,
                dict
            )
            and result.get(
                "status"
            ) in PENDING_STATUSES
        ):

            pending_action = result


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if (
            task.intent == "exit"
            or (
                task.data
                and task.data.get(
                    "action"
                ) == "exit"
            )
        ):

            send({
                "type": "exit_requested"
            })

            response_sent = True

            return


        # ----------------------------------------------------
        # CONVERSATION
        # ----------------------------------------------------

        conversation = (
            task.data.get(
                "conversation"
            )
            if task.data
            else None
        )


        if task.intent == "conversation":

            conversation = text


        if conversation:

            response = companion.chat(
                conversation,
                execution=result
            )

            if response:

                response = str(
                    response
                ).strip()

                if response:

                    send({
                        "type": "assistant_message",
                        "text": response
                    })

                    response_sent = True

                    return


        # ----------------------------------------------------
        # STRUCTURED EXECUTION RESULT
        # ----------------------------------------------------

        response_sent = (
            forward_result(
                result
            )
        )


        # ----------------------------------------------------
        # SAFE FALLBACK
        # ----------------------------------------------------

        if (
            not response_sent
            and pending_action is None
        ):

            send({
                "type": "assistant_message",
                "text": (
                    "I completed the request, "
                    "but I didn't receive a response "
                    "to display."
                )
            })

            response_sent = True


    except Exception as error:

        send({
            "type": "error",
            "text": str(error)
        })

        response_sent = True

        traceback.print_exc(
            file=sys.stderr
        )


    finally:

        sys.stdout = original_stdout


        # ----------------------------------------------------
        # Always end command cycle.
        # ----------------------------------------------------

        send({
            "type": "command_complete"
        })

        send({
            "type": "typing",
            "value": False
        })


# ============================================================
# MAIN LOOP
# ============================================================

def main():

    # --------------------------------------------------------
    # Initialize exactly once.
    # --------------------------------------------------------

    try:

        initialize_drax()

    except Exception as error:

        send({
            "type": "error",
            "text": (
                "Bridge initialization failed: "
                f"{error}"
            )
        })

        traceback.print_exc(
            file=sys.stderr
        )

        return


    # --------------------------------------------------------
    # Bridge ready.
    # --------------------------------------------------------

    send({
        "type": "ready"
    })


    # --------------------------------------------------------
    # JSONL COMMAND LOOP
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


        # ----------------------------------------------------
        # CHAT
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # PING
        # ----------------------------------------------------

        elif message_type == "ping":

            send({
                "type": "pong"
            })


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()