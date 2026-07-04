from core import understand
from executor import execute
from skills.skill_loader import load_skills
from skills.open_app import handle_pending_response
from resolver import get_cached_applications

print("=" * 35)
print("🤖 Welcome to DraxAgent v0.1")
print("=" * 35)

load_skills()

get_cached_applications()

pending_action = None


while True:

    user_input = input("\n> ")

    if pending_action:

        pending_action = handle_pending_response(
            pending_action,
            user_input
        )

        continue

    task = understand(user_input)

    result = execute(task)

    if result and result.get("status") in {
        "confirmation_required",
        "selection_required"
    }:
        pending_action = result

    if task.intent == "exit":
        break