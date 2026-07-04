import subprocess

from resolver import decide_application


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
            print(f"❌ Unknown application source: '{source}'.")
            return False

        print(f"🚀 Opening {app_name}...")
        return True

    except Exception as error:
        print(f"❌ Couldn't open '{app_name}'.")
        print(f"Reason: {error}")
        return False
    
def handle_pending_response(pending, user_input):

    response = user_input.lower().strip()

    if response in {"cancel", "stop", "nevermind", "never mind"}:
        print("👍 Okay, operation cancelled.")
        return None

    status = pending["status"]

    if status == "confirmation_required":

        if response in {"yes", "y", "yeah", "yep"}:
            launch_application(pending["match"])
            return None

        if response in {"no", "n", "nope"}:
            print("👍 Okay, cancelled.")
            return None

        print("🤖 Please answer yes or no.")
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
                print("👍 Okay, operation cancelled.")
                return None

        print(
            f"🤖 Choose a number from 1 to {cancel_number}, "
            f"or type 'cancel'."
        )
        return pending

    return None

def execute(task):

    query = task.data.get("target")

    if not query:
        print("❌ No application specified.")
        return

    decision = decide_application(query)

    status = decision["status"]

    if status == "resolved":
        launch_application(decision["match"])
        return

    if status == "confirm":
        match = decision["match"]

        print(f"🤖 Did you mean {match['name']}? (yes/no)")

        # Temporary return.
        # Next step: main.py will remember this confirmation.
        return {
            "status": "confirmation_required",
            "match": match
        }

    if status == "ambiguous":
        print("🤔 I found multiple possible applications:")

        candidates = [
            decision["match"],
            *decision["alternatives"]
        ]

        for index, candidate in enumerate(candidates, start=1):
            print(f"{index}. {candidate['name']}")
        
        print(f"{len(candidates) + 1}. Cancel operation")

        return {
            "status": "selection_required",
            "candidates": candidates
        }

    print(f"❌ I couldn't find an application matching '{query}'.")

    return {
        "status": "not_found"
    }