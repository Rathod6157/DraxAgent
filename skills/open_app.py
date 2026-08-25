import os
import subprocess

from terminal import (
    safe_print,
    status_print,
    success_print,
    error_print,
)

from resolver import decide_application
from brain.execution_result import ExecutionResult


NAME = "Open Application"
INTENT = "open_app"
DESCRIPTION = "Launches desktop applications."
VERSION = "1.4"
AUTHOR = "Harshith"


def launch_application(match):

    app_name = match["name"]
    launch_target = match["launch_target"]
    source = match["source"]

    try:

        # ---------------------------------
        # Start Menu applications
        # ---------------------------------

        if source == "start_menu":

            os.startfile(
                launch_target
            )

        # ---------------------------------
        # Windows Store / packaged apps
        # ---------------------------------

        elif source == "windows_app":

            subprocess.Popen(
                [
                    "explorer.exe",
                    f"shell:AppsFolder\\{launch_target}"
                ]
            )

        # ---------------------------------
        # Unknown source
        # ---------------------------------

        else:

            safe_print(
                f"❌ Unknown application source: '{source}'."
            )

            return ExecutionResult(
                handled=True,
                success=False
            )

        # ---------------------------------
        # Report success
        # ---------------------------------

        status_print(
            f"🚀 Opening {app_name}..."
        )

        success_print(
            f"{app_name.title()} opened."
        )

        return ExecutionResult(
            handled=True,
            success=True
        )

    except Exception as error:

        error_print(
            f"❌ Couldn't open '{app_name}'.\n"
            f"Reason: {error}"
        )

        return ExecutionResult(
            handled=True,
            success=False
        )


def handle_pending_response(
    pending,
    user_input
):

    response = user_input.lower().strip()

    cancel_words = {
        "cancel",
        "stop",
        "nevermind",
        "never mind"
    }

    yes_words = {
        "yes",
        "y",
        "yeah",
        "yep",
        "yup",
        "sure",
        "okay",
        "ok",
        "correct",
        "do it"
    }

    no_words = {
        "no",
        "n",
        "nope",
        "nah"
    }

    # ---------------------------------
    # Cancel
    # ---------------------------------

    if response in cancel_words:

        safe_print(
            "👍 Okay, operation cancelled."
        )

        return None

    status = pending["status"]

    # ---------------------------------
    # Normal application confirmation
    # ---------------------------------

    if status == "confirmation_required":

        if response in yes_words:

            launch_application(
                pending["match"]
            )

            return None

        if response in no_words:

            safe_print(
                "👍 Okay, cancelled."
            )

            return None

        safe_print(
            "🤖 Please answer yes or no."
        )

        return pending

    # ---------------------------------
    # Web fallback confirmation
    # ---------------------------------

    if status == "web_fallback_confirmation_required":

        if response in yes_words:

            from skills.open_web import execute as open_web

            task = pending["task"]

            return open_web(
                task
            )

        if response in no_words:

            safe_print(
                "👍 Okay, operation cancelled."
            )

            return None

        safe_print(
            "🤖 Please answer yes or no."
        )

        return pending

    # ---------------------------------
    # Application selection
    # ---------------------------------

    if status == "selection_required":

        candidates = pending["candidates"]

        cancel_number = len(candidates) + 1

        if response.isdigit():

            choice = int(response)

            if 1 <= choice <= len(candidates):

                launch_application(
                    candidates[choice - 1]
                )

                return None

            if choice == cancel_number:

                safe_print(
                    "👍 Operation cancelled."
                )

                return None

        safe_print(
            f"🤖 Choose a number from 1 to "
            f"{cancel_number}, or type 'cancel'."
        )

        return pending

    return None


def execute(task):

    data = task.data or {}

    query = (
        data.get("target")
        or task.target
        or ""
    ).strip()

    if not query:

        return ExecutionResult(
            handled=True,
            success=False,
            message="❌ No application specified."
        )

    # ---------------------------------
    # Resolve installed application
    # ---------------------------------

    decision = decide_application(
        query
    )

    status = decision["status"]

    # ---------------------------------
    # Application found confidently
    # ---------------------------------

    if status == "resolved":

        return launch_application(
            decision["match"]
        )

    # ---------------------------------
    # Application found, but confirmation
    # is required.
    # ---------------------------------

    if status == "confirm":

        match = decision["match"]

        safe_print(
            f"🤖 Did you mean "
            f"{match['name']}? (yes/no)"
        )

        return {
            "status": "confirmation_required",
            "match": match
        }

    # ---------------------------------
    # Multiple possible applications
    # ---------------------------------

    if status == "ambiguous":

        candidates = [
            decision["match"],
            *decision["alternatives"]
        ]

        lines = []

        lines.append(
            "🤔 I found multiple possible applications:"
        )

        lines.append("")

        for index, candidate in enumerate(
            candidates,
            start=1
        ):

            lines.append(
                f"{index}. {candidate['name']}"
            )

        lines.append("")

        lines.append(
            f"{len(candidates) + 1}. Cancel operation"
        )

        safe_print(
            "\n".join(lines)
        )

        return {
            "status": "selection_required",
            "candidates": candidates
        }

    # ---------------------------------
    # Application NOT found
    #
    # IMPORTANT:
    # Never silently turn an app request
    # into a web request.
    # ---------------------------------

    if status == "not_found":

        safe_print(
            f"🔎 I couldn't find an installed "
            f"application named '{query}'."
        )

        safe_print(
            f"🌐 Do you want me to open "
            f"'{query}' on the web instead? (yes/no)"
        )

        return {
            "status": "web_fallback_confirmation_required",
            "task": task
        }

    # ---------------------------------
    # Unexpected resolver status
    # ---------------------------------

    return ExecutionResult(
        handled=True,
        success=False,
        message=(
            f"❌ Couldn't determine how to open "
            f"'{query}'."
        )
    )