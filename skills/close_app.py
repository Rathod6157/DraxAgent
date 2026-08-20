import subprocess
import time

from resolver import decide_application
from terminal import (
    safe_print,
    status_print,
    status_done_print,
)


NAME = "Close Application"
INTENT = "close"
DESCRIPTION = "Closes running applications."
VERSION = "1.1"
AUTHOR = "Harshith"


PROCESS_ALIASES = {
    "clock": ["Time.exe"],
    "windows clock": ["Time.exe"],
    "calculator": ["CalculatorApp.exe"],
    "settings": ["SystemSettings.exe"],
    "snipping tool": ["SnippingTool.exe"],
    "snip": ["SnippingTool.exe"],
}


def close_application(match):

    app_name = match["name"]

    status_print(
        f"🔍 Looking for running processes matching "
        f"{app_name}..."
    )

    try:

        result = subprocess.run(
            [
                "tasklist",
                "/FO",
                "CSV",
                "/NH"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        process_lines = (
            result.stdout.lower().splitlines()
        )

        matches = []

        alias_processes = PROCESS_ALIASES.get(
            app_name.lower()
        )

        if alias_processes:

            for line in process_lines:

                process_name = (
                    line.split(",")[0]
                    .strip('"')
                )

                if any(
                    process_name.lower()
                    == alias.lower()
                    for alias in alias_processes
                ):

                    if process_name not in matches:

                        matches.append(
                            process_name
                        )

        else:

            search_words = (
                app_name.lower().split()
            )

            for line in process_lines:

                process_name = (
                    line.split(",")[0]
                    .strip('"')
                )

                if any(
                    word in process_name.lower()
                    for word in search_words
                ):

                    if process_name not in matches:

                        matches.append(
                            process_name
                        )

        if not matches:

            safe_print(
                f"❌ I couldn't find a running "
                f"process for {app_name}."
            )

            return False

        # ---------------------------------
        # Single confirmation message
        # ---------------------------------
        status_done_print(
            f"🤔 Found {len(matches)} running process."
            if len(matches) == 1
            else f"🤔 Found {len(matches)} running processes."
        )
        
        lines = []

        lines.append(
            "🤔 Possible running processes:"
        )

        lines.append("")

        for index, process_name in enumerate(
            matches,
            start=1
        ):

            lines.append(
                f"{index}. {process_name}"
            )

        lines.append("")

        lines.append(
            f"🤖 Close {app_name}? (yes/no)"
        )

        safe_print(
            "\n".join(lines)
        )

        return {
            "status": "close_confirmation_required",
            "app_name": app_name,
            "processes": matches
        }

    except Exception as error:

        safe_print(
            f"❌ Couldn't inspect running "
            f"processes: {error}"
        )

        return False


def is_process_running(
    process_name
):

    result = subprocess.run(
        [
            "tasklist",
            "/FI",
            f"IMAGENAME eq {process_name}",
            "/NH"
        ],
        capture_output=True,
        text=True
    )

    return (
        process_name.lower()
        in result.stdout.lower()
    )


def handle_pending_response(
    pending,
    user_input
):

    response = user_input.lower().strip()

    # ---------------------------------
    # Cancel
    # ---------------------------------

    if response in {
        "cancel",
        "stop",
        "nevermind",
        "never mind",
        "no",
        "n",
        "nope"
    }:

        safe_print(
            "👍 Okay, close operation cancelled."
        )

        return None

    # ---------------------------------
    # Invalid response
    # ---------------------------------

    if response not in {
        "yes",
        "y",
        "yeah",
        "yep",
        "sure",
        "okay",
        "ok"
    }:

        safe_print(
            "🤖 Please answer yes or no."
        )

        return pending

    processes = pending["processes"]

    app_name = pending["app_name"]

    closed_any = False

    status_print(
        f"🛑 Closing {app_name}..."
    )

    for process_name in processes:

        subprocess.run(
            ["taskkill", "/IM", process_name, "/F"],
            capture_output=True,
            text=True
        )

        time.sleep(0.5)

        if is_process_running(process_name):

            status_done_print(
                f"❌ Couldn't close {process_name}."
            )

        else:

            status_done_print(
                f"✅ Closed {process_name}."
            )

            closed_any = True


    if closed_any:

        status_done_print(
            f"👋 Finished closing {app_name}."
        )

    else:

        status_done_print(
            f"❌ Couldn't close {app_name}."
        )

    return None


def execute(task):

    query = task.data.get(
        "target"
    )

    if not query:

        safe_print(
            "❌ No application specified."
        )

        return

    decision = decide_application(
        query
    )

    status = decision["status"]

    # ---------------------------------
    # Resolved
    # ---------------------------------

    if status == "resolved":

        return close_application(
            decision["match"]
        )

    # ---------------------------------
    # Confirmation required
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
    # Ambiguous
    # ---------------------------------

    if status == "ambiguous":

        candidates = [
            decision["match"],
            *decision["alternatives"]
        ]

        lines = []

        lines.append(
            "🤔 I found multiple possible "
            "applications:"
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
            f"{len(candidates) + 1}. "
            f"Cancel operation"
        )

        safe_print(
            "\n".join(lines)
        )

        return {
            "status": "selection_required",
            "candidates": candidates
        }

    # ---------------------------------
    # Not found
    # ---------------------------------

    safe_print(
        f"❌ I couldn't safely determine "
        f"which application to close."
    )

    return {
        "status": "not_found"
    }