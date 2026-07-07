import importlib
import os
from terminal import safe_print

SKILLS = {}


def load_skills():

    folder = os.path.dirname(__file__)

    for file in os.listdir(folder):

        if file.endswith(".py"):

            if file.startswith("__"):

                continue

            if file == "skill_loader.py":

                continue

            module_name = file[:-3]

            module = importlib.import_module(f"skills.{module_name}")

            if hasattr(module, "INTENT"):

                SKILLS[module.INTENT] = module
                
                safe_print(f"✅ Loaded skill: {module.NAME}")


def get_skill(intent):

    return SKILLS.get(intent)

def get_all_skills():
    return SKILLS.values()

def show_loaded_capabilities():
    if not SKILLS:
        safe_print("🤖 No capabilities loaded.")
        return

    safe_print("\n🤖 What I can do:")

    for skill in SKILLS.values():
        name = getattr(skill, "NAME", "Unknown Skill")
        description = getattr(skill, "DESCRIPTION", "No description available.")

        safe_print(f"   • {name}: {description}")

    safe_print("\n💡 Try commands like:")
    safe_print("   • open chrome")
    safe_print("   • close calculator")
    safe_print("   • set a timer for 10 seconds")
    safe_print("   • set a timer for 1 minute called study")
    safe_print("   • list timers")
    safe_print("   • cancel timer 1")
    safe_print("   • exit")

def get_loaded_skills():
    return list(SKILLS.values())