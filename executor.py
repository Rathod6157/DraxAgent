from models import Task
from skills.skill_loader import get_skill


def execute(task: Task):

    if task.intent == "greeting":
        print("Hey Harshith! 👋")

    elif task.intent == "exit":
        print("Goodbye! 👋")
        
    elif task.intent == "cancelled":
        print("👍 Okay, I won't do that.")
    
    else:

        skill = get_skill(task.intent)

        if skill:

            return skill.execute(task)

        else:

            print("I don't understand that yet.")

