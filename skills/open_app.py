import subprocess
from terminal import safe_print
from resolver import decide_application
from terminal import safe_print


NAME = "Open Application"
INTENT = "open"
DESCRIPTION = "Launches desktop applications."
VERSION = "1.1"
AUTHOR = "Harshith"


def launch_application(match):

    app_name = match["name"]
    launch_target = match["launch_target"]
    source = match["source"]

    try:

        if source == "start_menu":
            subprocess.Popen(
                launch_target,
                shell=True
            )

        elif source == "windows_app":
            subprocess.Popen(
                [
                    "explorer.exe",
                    f"shell:AppsFolder\\{launch_target}"
                ]
            )

        else:
            safe_print(f"❌ Unknown application source: '{source}'.")
            return False

        safe_print(f"🚀 Opening {app_name}...")
        safe_print(f"✅ {app_name.title()} opened.")
        return True

    except Exception as error:
        safe_print(f"❌ Couldn't open '{app_name}'.")
        safe_print(f"Reason: {error}")
        return False
    
def handle_pending_response(pending, user_input):

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

    if response in cancel_words:
        safe_print("👍 Okay, operation cancelled.")
        return None

    status = pending["status"]

    if status == "confirmation_required":

        if response in yes_words:
            launch_application(pending["match"])
            return None

        if response in no_words:
            safe_print("👍 Okay, cancelled.")
            return None

        safe_print("🤖 Please answer yes or no.")
        return pending

    if status == "selection_required":

        candidates = pending["candidates"]
        cancel_number = len(candidates) + 1

        if response.isdigit():

            choice = int(response)

            if 1 <= choice <= len(candidates):
                launch_application(candidates[choice - 1])
                return None

            if choice == cancel_number:
                safe_print("👍 Okay, operation cancelled.")
                return None

        safe_print(
            f"🤖 Choose a number from 1 to {cancel_number}, "
            f"or type 'cancel'."
        )

        return pending

    return None

def execute(task):

    query = task.data.get("target")

    if not query:
        safe_print("❌ No application specified.")
        return

    decision = decide_application(query)

    status = decision["status"]

    if status == "resolved":
        launch_application(decision["match"])
        return

    if status == "confirm":
        match = decision["match"]

        safe_print(f"🤖 Did you mean {match['name']}? (yes/no)")

        # Temporary return.
        # Next step: main.py will remember this confirmation.
        return {
            "status": "confirmation_required",
            "match": match
        }

    if status == "ambiguous":
        safe_print("🤔 I found multiple possible applications:")

        candidates = [
            decision["match"],
            *decision["alternatives"]
        ]

        for index, candidate in enumerate(candidates, start=1):
            safe_print(f"{index}. {candidate['name']}")
        
        safe_print(f"{len(candidates) + 1}. Cancel operation")

        return {
            "status": "selection_required",
            "candidates": candidates
        }

    safe_print(f"❌ I couldn't find an application matching '{query}'.")

    return {
        "status": "not_found"
    }