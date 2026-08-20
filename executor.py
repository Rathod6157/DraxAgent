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

        success = all(
            item["result"].success
            for item in results
            if isinstance(
                item["result"],
                ExecutionResult
            )
        )

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
            exit_requested=True,
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
    # Pending skill operation
    # -----------------------

    if isinstance(
        result,
        dict
    ):

        status = result.get(
            "status"
        )

        if status in {
            "confirmation_required",
            "selection_required",
            "close_confirmation_required"
        }:

            # IMPORTANT:
            # Return the pending operation directly.
            #
            # ConversationEngine will remember it
            # and route the user's next message
            # ("yes", "no", "1", etc.) back to
            # the correct skill handler.

            return result


        # -----------------------
        # Other dictionary result
        # -----------------------

        return ExecutionResult(
            handled=True,
            success=False,
            data=result
        )


    # -----------------------
    # Old-style skill
    # -----------------------

    return ExecutionResult(
        handled=True,
        success=True
    )