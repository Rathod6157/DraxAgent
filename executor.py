from models import Task
from skills.skill_loader import get_skill

from brain.execution_result import ExecutionResult
from brain.visual_bridge import visual_bridge


def _file_operation(task):

    from file_access import inspect, search

    query = (
        task.target
        or task.data.get("target")
        or task.data.get("file")
        or ""
    ).strip()

    raw = (
        task.data.get("raw_command")
        or ""
    ).strip()

    effective_query = query or raw

    if not effective_query:

        return ExecutionResult(
            handled=True,
            success=False,
            message=(
                "I need to know which file "
                "you want me to inspect."
            ),
            data={
                "file_context": {
                    "success": False,
                    "kind": "file",
                },
                "ai_response": True,
            },
        )


    # =================================================
    # FILE SEARCH
    # =================================================

    if task.intent == "file_search":

        result = search(
            effective_query
        )

        return ExecutionResult(
            handled=True,
            success=result.get(
                "success",
                False
            ),
            message=result.get(
                "message",
                ""
            ),
            data={
                "file_context": result,
                "ai_response": True,
            },
        )


    # =================================================
    # FILE INSPECTION
    # =================================================

    result = inspect(
        effective_query,
        include_related=True,
    )

    return ExecutionResult(
        handled=True,
        success=result.get(
            "success",
            False
        ),
        message=result.get(
            "message",
            ""
        ),
        data={
            "file_context": result,
            "ai_response": True,
        },
    )


def _app_status(task):

    from app_monitor import status

    target = (
        task.target
        or task.data.get("target")
        or ""
    ).strip()

    if not target:

        return ExecutionResult(
            handled=True,
            success=False,
            message=(
                "I need an application "
                "to check."
            ),
            data={
                "app_status": {
                    "success": False,
                    "message": (
                        "No application supplied."
                    ),
                },
                "ai_response": True,
            },
        )

    result = status(
        target
    )

    return ExecutionResult(
        handled=True,
        success=result.get(
            "success",
            False
        ),
        message=result.get(
            "message",
            ""
        ),
        data={
            "app_status": result,
            "ai_response": True,
        },
    )


def _wait_for_app(task):

    from app_monitor import (
        watch_until_responsive
    )

    target = (
        task.target
        or task.data.get("target")
        or ""
    ).strip()

    if not target:

        return ExecutionResult(
            handled=True,
            success=False,
            message=(
                "I need an application "
                "to watch."
            ),
        )

    raw = (
        task.data.get("raw_command")
        or ""
    ).lower()

    timeout = 300
    interval = 2.0

    if "minute" in raw:

        import re

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*minutes?",
            raw,
        )

        if match:

            timeout = max(
                10,
                float(match.group(1)) * 60,
            )

    elif "second" in raw:

        import re

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*seconds?",
            raw,
        )

        if match:

            timeout = max(
                5,
                float(match.group(1)),
            )


    watch_until_responsive(
        target,
        timeout=timeout,
        interval=interval,
    )

    return ExecutionResult(
        handled=True,
        success=True,
        message=(
            f"👀 I'm watching '{target}'. "
            "I'll tell you when it responds again."
        ),
        data={
            "watching": True,
            "target": target,
            "timeout": timeout,
            "interval": interval,
        },
    )


def execute(task: Task):

    # =================================================
    # COMPOUND COMMAND
    # =================================================

    if task.intent == "compound":

        results = []
        conversation_tasks = []

        for child_task in task.data.get(
            "tasks",
            []
        ):

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
                "result": child_result,
            })


        success = all(
            item["result"].success
            for item in results
            if isinstance(
                item["result"],
                ExecutionResult,
            )
        )

        handled = bool(
            results
        )

        return ExecutionResult(
            handled=handled,
            success=success,
            data={
                "results": results,
                "conversation_tasks": (
                    conversation_tasks
                ),
            },
        )


    # =================================================
    # GREETING
    # =================================================

    if task.intent == "greeting":

        return ExecutionResult(
            handled=False,
        )


    # =================================================
    # EXIT
    # =================================================

    if task.intent == "exit":

        return ExecutionResult(
            handled=True,
            success=True,
            exit_requested=True,
        )


    # =================================================
    # CANCELLED
    # =================================================

    if task.intent == "cancelled":

        return ExecutionResult(
            handled=True,
            success=True,
            message=(
                "👍 Okay, I won't do that."
            ),
        )


    # =================================================
    # FILE INTELLIGENCE
    # =================================================

    if task.intent in {
        "file_search",
        "file_inspect",
    }:

        return _file_operation(
            task
        )


    # =================================================
    # APPLICATION STATUS
    # =================================================

    if task.intent == "app_status":

        return _app_status(
            task
        )


    # =================================================
    # WAIT FOR APPLICATION
    # =================================================

    if task.intent == "wait_for_app":

        return _wait_for_app(
            task
        )


    # =================================================
    # VISUAL OBSERVATION
    # =================================================

    if task.intent == "visual_observe":

        result = visual_bridge.observe(
            instruction=(
                task.data.get(
                    "raw_command"
                )
                or
                "Describe the current desktop."
            )
        )

        if not result.get(
            "success",
            False
        ):

            return ExecutionResult(
                handled=True,
                success=False,
                message=(
                    "I couldn't understand "
                    "the current screen."
                ),
                data=result,
            )


        vision = result.get(
            "vision",
            {}
        )

        summary = vision.get(
            "summary",
            "I can see the current desktop.",
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
            message=" ".join(
                message_parts
            ),
            data=result,
        )


    # =================================================
    # VISUAL CLICK
    # =================================================

    if task.intent == "visual_click":

        target = (
            task.target
            or task.data.get("target")
        )

        if not target:

            return ExecutionResult(
                handled=True,
                success=False,
                message=(
                    "I need to know what "
                    "you want me to click."
                ),
            )


        result = visual_bridge.click(
            target
        )

        if not result.get(
            "success",
            False
        ):

            return ExecutionResult(
                handled=True,
                success=False,
                message=(
                    f"I couldn't successfully "
                    f"click '{target}'."
                ),
                data=result,
            )


        return ExecutionResult(
            handled=True,
            success=True,
            message=(
                f"Clicked '{target}' "
                "and verified the screen."
            ),
            data=result,
        )


    # =================================================
    # EXISTING SKILLS
    # =================================================

    skill = get_skill(
        task.intent
    )

    if not skill:

        return ExecutionResult(
            handled=False,
        )


    result = skill.execute(
        task
    )


    if isinstance(
        result,
        ExecutionResult
    ):

        return result


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
            "close_confirmation_required",
        }:

            return result


        return ExecutionResult(
            handled=True,
            success=False,
            data=result,
        )


    return ExecutionResult(
        handled=True,
        success=True,
    )