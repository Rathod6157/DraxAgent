from models import Task
from skills.skill_loader import get_skill
from terminal import safe_print

def execute(task: Task):

    if task.intent == "greeting":
        safe_print("Hey Harshith! 👋")

    elif task.intent == "exit":
        safe_print("Goodbye! 👋")
        
    elif task.intent == "cancelled":
        safe_print("👍 Okay, I won't do that.")
    
    else:

        skill = get_skill(task.intent)

        if skill:

            return skill.execute(task)

        else:

            safe_print("I don't understand that yet.")

