from models import Task
from skills.skill_loader import get_skill

from brain.execution_result import ExecutionResult


def execute(task: Task):

    # -----------------------
    # Compound command
    # -----------------------

    if task.intent == "compound":

        results = []
        conversation_tasks = []

        for child_task in task.data.get("tasks", []):

            # Conversation parts should NOT be executed
            # as skills. They will be sent to Drax later.
            if child_task.intent == "conversation":

                conversation_tasks.append(
                    child_task
                )

                continue

            child_result = execute(
                child_task
            )

            results.append({
                "task": child_task,
                "result": child_result
            })

        # A compound command is considered successful
        # if every executable action succeeded.
        success = all(
            item["result"].success
            for item in results
        )

        # If there were no executable actions,
        # let the conversational brain handle it.
        handled = bool(results)

        return ExecutionResult(
            handled=handled,
            success=success,
            data={
                "results": results,
                "conversation_tasks": conversation_tasks
            }
        )

    # -----------------------
    # Greeting
    # -----------------------

    if task.intent == "greeting":

        return ExecutionResult(
            handled=False
        )

    # -----------------------
    # Exit
    # -----------------------

    if task.intent == "exit":

        return ExecutionResult(
            handled=True,
            success=True,
            message="Goodbye! 👋"
        )

    # -----------------------
    # Cancelled
    # -----------------------

    if task.intent == "cancelled":

        return ExecutionResult(
            handled=True,
            success=True,
            message="👍 Okay, I won't do that."
        )

    # -----------------------
    # Skills
    # -----------------------

    skill = get_skill(
        task.intent
    )

    if not skill:

        return ExecutionResult(
            handled=False
        )

    result = skill.execute(
        task
    )

    # -----------------------
    # New-style skill
    # -----------------------

    if isinstance(
        result,
        ExecutionResult
    ):

        return result

    # -----------------------
    # Old-style skill
    # -----------------------

    return ExecutionResult(
        handled=True,
        success=True
    )