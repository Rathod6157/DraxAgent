from core import understand
from executor import execute
from skills.skill_loader import load_skills
from skills.open_app import handle_pending_response
from resolver import get_cached_applications
from terminal import terminal_session
from prompt_toolkit import prompt
from skills.close_app import handle_pending_response as handle_close_response

print("=" * 35)
print("🤖 Welcome to DraxAgent v0.1")
print("=" * 35)

load_skills()

get_cached_applications()

pending_action = None

with terminal_session():
    while True:

        user_input = prompt("\n> ")

        if pending_action:

            if pending_action["status"] == "close_confirmation_required":
                pending_action = handle_close_response(
                    pending_action,
                    user_input
                )

            else:
                pending_action = handle_pending_response(
                    pending_action,
                    user_input
                )

            continue

        task = understand(user_input)

        result = execute(task)

        if result and result.get("status") in {
            "confirmation_required",
            "selection_required",
            "close_confirmation_required"
        }:
            pending_action = result
            
        if task.intent == "exit" or task.data.get("action") == "exit":
            break