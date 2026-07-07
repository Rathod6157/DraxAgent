from skills.skill_loader import get_loaded_skills
from terminal import safe_print


NAME = "Help"
INTENT = "help"
DESCRIPTION = "Shows available features and example commands."
VERSION = "1.0"
AUTHOR = "Harshith"


def execute(task):
    safe_print("\n🤖 What I can do:")

    for skill in get_loaded_skills():
        name = getattr(skill, "NAME", "Unknown Skill")
        description = getattr(
            skill,
            "DESCRIPTION",
            "No description available."
        )

        safe_print(f"   • {name}: {description}")

    safe_print("   • open chrome")
    safe_print("   • close calculator")

    safe_print("   • is chrome running")
    safe_print("   • is settings open")
    safe_print("   • what apps are running")
    safe_print("   • show open windows")

    safe_print("   • set a timer for 10 seconds")
    safe_print("   • set a timer for 1 minute called study")
    safe_print("   • list timers")
    safe_print("   • cancel timer study")

    safe_print("   • help")
    safe_print("   • exit")