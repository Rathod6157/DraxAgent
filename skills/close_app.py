import subprocess
import time
from resolver import decide_application
from terminal import safe_print


NAME = "Close Application"
INTENT = "close"
DESCRIPTION = "Closes running applications."
VERSION = "1.0"
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

    safe_print(f"🔍 Looking for running processes matching {app_name}...")

    try:
        result = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            check=True
        )

        process_lines = result.stdout.lower().splitlines()

        matches = []

        alias_processes = PROCESS_ALIASES.get(app_name.lower())

        if alias_processes:

            for line in process_lines:

                process_name = line.split(",")[0].strip('"')

                if any(
                    process_name.lower() == alias.lower()
                    for alias in alias_processes
                ):
                    if process_name not in matches:
                        matches.append(process_name)

        else:

            search_words = app_name.lower().split()

            for line in process_lines:

                process_name = line.split(",")[0].strip('"')

                if any(word in process_name.lower() for word in search_words):
                    if process_name not in matches:
                        matches.append(process_name)

        if not matches:
            safe_print(f"❌ I couldn't find a running process for {app_name}.")
            return False

        safe_print("🤔 Possible running processes:")

        for index, process_name in enumerate(matches, start=1):
            safe_print(f"{index}. {process_name}")
        
        safe_print(f"🤖 Close {app_name}? (yes/no)")

        return {
            "status": "close_confirmation_required",
            "app_name": app_name,
            "processes": matches
        }

    except Exception as error:
        safe_print(f"❌ Couldn't inspect running processes: {error}")
        return False

def is_process_running(process_name):

    result = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {process_name}", "/NH"],
        capture_output=True,
        text=True
    )

    return process_name.lower() in result.stdout.lower()


def handle_pending_response(pending, user_input):

    response = user_input.lower().strip()

    if response in {
        "cancel", "stop", "nevermind", "never mind",
        "no", "n", "nope"
    }:
        safe_print("👍 Okay, close operation cancelled.")
        return None

    if response not in {
        "yes", "y", "yeah", "yep",
        "sure", "okay", "ok"
    }:
        safe_print("🤖 Please answer yes or no.")
        return pending

    processes = pending["processes"]
    app_name = pending["app_name"]

    closed_any = False

    for process_name in processes:

        subprocess.run(
            ["taskkill", "/IM", process_name, "/F"],
            capture_output=True,
            text=True
        )

        time.sleep(0.5)

        if is_process_running(process_name):
            safe_print(f"❌ {process_name} is still running.")
        else:
            safe_print(f"✅ Closed {process_name}.")
            closed_any = True

    if closed_any:
        safe_print(f"👋 Finished closing {app_name}.")
    else:
        safe_print(f"❌ Couldn't close {app_name}.")

    return None
def execute(task):

    query = task.data.get("target")

    if not query:
        safe_print("❌ No application specified.")
        return

    decision = decide_application(query)

    status = decision["status"]

    if status == "resolved":
        return close_application(decision["match"])

    safe_print(
        f"❌ Couldn't safely determine which application to close."
    )