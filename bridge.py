import sys
import json
import traceback
import os
import threading

# Tell the existing Drax terminal system that
# we are running through the Tauri bridge.
os.environ["DRAX_BRIDGE"] = "1"


# ============================================================
# BRIDGE STDOUT
# ============================================================

# stdout belongs exclusively to the Tauri JSON protocol.
BRIDGE_STDOUT = sys.stdout

# Activity and command events can arrive from different Python
# threads. Serialize JSONL writes so messages can never interleave.
SEND_LOCK = threading.Lock()

# Normal Python/debug output must never contaminate JSONL.
sys.stdout = sys.stderr


# ============================================================
# JSON OUTPUT
# ============================================================

def send(message):
    """
    Send one JSON event to the Tauri frontend.

    IMPORTANT:
    Always write directly to the original bridge stdout.
    """

    with SEND_LOCK:

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
    Forward Drax's existing terminal output system
    into the Tauri frontend.
    """

    if text is None:
        return

    send({
        "type": "output",
        "message_type": str(message_type),
        "text": str(text)
    })


# ============================================================
# PENDING ACTIONS
# ============================================================

# The old terminal main.py keeps this state between commands.
# The bridge must do the same, otherwise confirmations such as:
#
#   "Did you mean Chrome? (yes/no)"
#   "Close Clock? (yes/no)"
#
# are lost when the next message arrives.
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
    Route a pending confirmation/selection to the same
    skill-specific handlers used by main.py.

    Returns:
        The updated pending action, or None when finished.
    """

    status = pending.get("status")

    # Close-app has its own confirmation handler.
    if status == "close_confirmation_required":

        from skills.close_app import (
            handle_pending_response
        )

        return handle_pending_response(
            pending,
            user_input
        )

    # Open-app handles:
    # - normal application confirmation
    # - application selection
    # - web fallback confirmation
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
    Forward structured results that do not already arrive
    through terminal.py's output callback.
    """

    if result is None:
        return

    # ExecutionResult-style object.
    message = getattr(
        result,
        "message",
        None
    )

    if message:
        message = str(message).strip()

        if message:
            send({
                "type": "assistant_message",
                "text": message
            })

        return

    # Dictionary-style result.
    if isinstance(result, dict):

        message = result.get(
            "message"
        )

        if message:
            send({
                "type": "assistant_message",
                "text": str(message).strip()
            })

            return

        status = result.get(
            "status"
        )

        if (
            status
            and status not in PENDING_STATUSES
        ):

            send({
                "type": "status_done",
                "text": str(status).replace(
                    "_",
                    " "
                ).capitalize()
            })


# ============================================================
# COMMAND HANDLER
# ============================================================

def handle_command(text):

    global pending_action

    # --------------------------------------------------------
    # IMPORTANT
    #
    # Drax's terminal.py uses Prompt Toolkit for the normal
    # terminal UI. The Tauri child process does not own a real
    # interactive console.
    #
    # Therefore:
    #
    #   stdout -> Tauri JSON protocol
    #   stderr -> old terminal/debug output
    #
    # The existing terminal callback still forwards useful
    # skill messages to the frontend.
    # --------------------------------------------------------

    original_stdout = sys.stdout

    try:

        # Keep bridge JSON isolated on stdout.
        sys.stdout = sys.stderr

        # ----------------------------------------------------
        # Import the REAL Drax execution pipeline.
        #
        # This intentionally mirrors main.py instead of calling
        # drax.chat() directly.
        #
        # That is important because main.py owns:
        #
        #   understand -> execute -> pending skill handling
        #
        # Calling only drax.chat() bypassed that terminal-level
        # skill lifecycle.
        # ----------------------------------------------------

        from core import understand
        from executor import execute

        from brain.companion import (
            companion
        )

        # ----------------------------------------------------
        # Thinking
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
        #
        # This MUST happen before normal understanding.
        #
        # Example:
        #
        #   User: "Close Clock"
        #   Drax: "Close Clock? (yes/no)"
        #   User: "yes"
        #
        # The "yes" belongs to close_app, not to the AI router.
        # ----------------------------------------------------

        if pending_action is not None:

            pending_action = handle_pending_action(
                pending_action,
                text
            )

            return

        # ----------------------------------------------------
        # NORMAL UNDERSTANDING
        # ----------------------------------------------------

        task = understand(
            text
        )

        # ----------------------------------------------------
        # EXECUTION
        # ----------------------------------------------------

        result = execute(
            task
        )

        # ----------------------------------------------------
        # STORE PENDING OPERATION
        # ----------------------------------------------------

        if (
            isinstance(result, dict)
            and result.get("status")
            in PENDING_STATUSES
        ):

            pending_action = result

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if (
            task.intent == "exit"
            or (
                task.data
                and task.data.get("action") == "exit"
            )
        ):

            send({
                "type": "exit_requested"
            })

            return

        # ----------------------------------------------------
        # CONVERSATION
        #
        # Same behavior as main.py:
        # pure conversation and action+conversation both go
        # through Companion.
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

                send({
                    "type": "assistant_message",
                    "text": str(response).strip()
                })

                return

        # ----------------------------------------------------
        # STRUCTURED RESULT
        # ----------------------------------------------------

        forward_result(
            result
        )

    except Exception as error:

        send({
            "type": "error",
            "text": str(error)
        })

        traceback.print_exc(
            file=sys.stderr
        )

    finally:

        sys.stdout = original_stdout

        send({
            "type": "typing",
            "value": False
        })


# ============================================================
# MAIN LOOP
# ============================================================

def main():

    # --------------------------------------------------------
    # ONE-TIME RUNTIME INITIALIZATION
    # --------------------------------------------------------
    # Skills are loaded before the frontend output callback is
    # installed. This keeps normal startup messages out of chat.
    # The activity observer is also started exactly once here.
    # --------------------------------------------------------

    try:

        from terminal import set_output_callback
        from skills.skill_loader import load_skills
        from resolver import get_cached_applications
        from brain.event_bus import bus
        from brain import observer
        from brain.activity_engine import activity_engine  # noqa: F401

        # Load skills while stdout is still routed to stderr.
        load_skills()
        get_cached_applications()

        # Only after startup noise is finished do we bridge terminal
        # output into the Tauri chat.
        set_output_callback(
            frontend_output
        )

        # ----------------------------------------------------
        # LIVE DESKTOP ACTIVITY -> TAURI
        # ----------------------------------------------------

        def forward_activity_context(data):
            if not isinstance(data, dict):
                return

            send({
                "type": "activity_context",
                "application": data.get("application"),
                "process": data.get("process"),
                "window": data.get("window"),
                "executable": data.get("executable"),
                "observed_at": data.get("observed_at"),
            })

        def forward_activity_update(data):
            if not isinstance(data, dict):
                return

            send({
                "type": "activity_updated",
                "activity": data.get("activity"),
                "confidence": data.get("confidence"),
                "application": data.get("application"),
                "process": data.get("process"),
                "window": data.get("window"),
                "started_at": data.get("started_at"),
                "context": data.get("context", ""),
                "visual_context": data.get("visual_context"),
            })

        bus.subscribe(
            "activity_context",
            forward_activity_context
        )

        bus.subscribe(
            "activity_updated",
            forward_activity_update
        )

        # Keep a reference so the imported engine cannot be optimized
        # away or accidentally initialized by a different path.
        _ = activity_engine

        # Tell the webview that the bridge is ready first. The tiny
        # delay gives the JS event listener time to attach before the
        # observer emits its initial foreground-window event.
        send({
            "type": "ready"
        })

        def start_observer():
            try:
                import time
                time.sleep(0.75)
                observer.start()
            except Exception as error:
                print(
                    f"Activity observer failed to start: {error}",
                    file=sys.stderr
                )

        threading.Thread(
            target=start_observer,
            name="drax-activity-observer",
            daemon=True
        ).start()

    except Exception as error:

        print(
            f"Bridge initialization warning: {error}",
            file=sys.stderr
        )

        send({
            "type": "error",
            "text": f"Drax initialization failed: {error}"
        })

        return

    send({
        "type": "ready"
    })

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
