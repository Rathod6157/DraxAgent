from models import Task
from skills.skill_loader import get_skill

from brain.execution_result import ExecutionResult

from brain.visual_bridge import visual_bridge

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
    # Visual observation
    # -----------------------

    if task.intent == "visual_observe":

        result = visual_bridge.observe(
            instruction=(
                task.data.get("raw_command")
                or "Describe the current desktop."
            )
        )

        if not result.get("success", False):

            return ExecutionResult(
                handled=True,
                success=False,
                message=(
                    "I couldn't understand the current screen."
                ),
                data=result
            )

        vision = result.get(
            "vision",
            {}
        )

        summary = vision.get(
            "summary",
            "I can see the current desktop."
        )

        application = vision.get(
            "application"
        )

        text = vision.get(
            "text",
            []
        )

        message_parts = [
            summary
        ]

        if application:
            message_parts.append(
                f"Main application: {application}."
            )

        if text:
            visible_text = ", ".join(
                str(item)
                for item in text[:12]
            )

            message_parts.append(
                f"Visible text: {visible_text}."
            )

        return ExecutionResult(
            handled=True,
            success=True,
            message=" ".join(message_parts),
            data=result
        )


    # -----------------------
    # Visual click
    # -----------------------

    if task.intent == "visual_click":

        target = (
            task.target
            or task.data.get("target")
        )

        if not target:

            return ExecutionResult(
                handled=True,
                success=False,
                message="I need to know what you want me to click."
            )

        result = visual_bridge.click(
            target
        )

        if not result.get("success", False):

            return ExecutionResult(
                handled=True,
                success=False,
                message=(
                    f"I couldn't successfully click "
                    f"'{target}'."
                ),
                data=result
            )

        return ExecutionResult(
            handled=True,
            success=True,
            message=(
                f"Clicked '{target}' and verified the screen."
            ),
            data=result
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