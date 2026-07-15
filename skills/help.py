from skills.skill_loader import get_loaded_skills
from terminal import safe_print


NAME = "Help"
INTENT = "help"
DESCRIPTION = "Shows available features and example commands."
VERSION = "1.0"
AUTHOR = "Harshith"


def execute(task):

    lines = []

    lines.append("🤖 What I can do:")
    lines.append("")

    for skill in get_loaded_skills():
        name = getattr(skill, "NAME", "Unknown Skill")
        description = getattr(
            skill,
            "DESCRIPTION",
            "No description available."
        )

        lines.append(f"• {name}: {description}")

    lines.append("")
    lines.append("💡 Try commands like:")
    lines.append("")

    lines.append("• open chrome")
    lines.append("• close calculator")

    lines.append("")

    lines.append("• is chrome running")
    lines.append("• is settings open")
    lines.append("• what apps are running")
    lines.append("• show open windows")

    lines.append("")

    lines.append("• set a timer for 10 seconds")
    lines.append("• set a timer for 1 minute called study")
    lines.append("• list timers")
    lines.append("• cancel timer study")

    lines.append("")

    lines.append("• help")
    lines.append("• exit")

    safe_print("\n".join(lines))