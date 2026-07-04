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