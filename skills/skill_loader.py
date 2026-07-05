import importlib
import os

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
                
                print(f"✅ Loaded skill: {module.NAME}")


def get_skill(intent):

    return SKILLS.get(intent)

def get_all_skills():
    return SKILLS.values()

def show_loaded_capabilities():
    if not SKILLS:
        print("🤖 No capabilities loaded.")
        return

    print("\n🤖 What I can do:")

    for skill in SKILLS.values():
        name = getattr(skill, "NAME", "Unknown Skill")
        description = getattr(skill, "DESCRIPTION", "No description available.")

        print(f"   • {name}: {description}")

    print("\n💡 Try commands like:")
    print("   • open chrome")
    print("   • close calculator")
    print("   • set a timer for 10 seconds")
    print("   • set a timer for 1 minute called study")
    print("   • list timers")
    print("   • cancel timer 1")
    print("   • exit")