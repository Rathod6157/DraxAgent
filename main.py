from core import understand
from executor import execute

from skills.skill_loader import (
    load_skills,
    show_loaded_capabilities
)

from skills.open_app import (
    handle_pending_response
)

from resolver import (
    get_cached_applications
)

from terminal import (
    terminal_session,
    safe_print
)

from prompt_toolkit import prompt

from skills.close_app import (
    handle_pending_response as handle_close_response
)

from brain.companion import companion


safe_print("=" * 35)
safe_print("🤖 Welcome to DraxAgent v0.1")
safe_print("=" * 35)


load_skills()

show_loaded_capabilities()

get_cached_applications()


pending_action = None


with terminal_session():

    while True:

        user_input = prompt("\n> ")

        # -----------------------------------------
        # Handle pending skill operation
        # -----------------------------------------

        if pending_action:

            if (
                pending_action["status"]
                == "close_confirmation_required"
            ):

                pending_action = (
                    handle_close_response(
                        pending_action,
                        user_input
                    )
                )

            else:

                pending_action = (
                    handle_pending_response(
                        pending_action,
                        user_input
                    )
                )

            continue


        # -----------------------------------------
        # Understand user message
        # -----------------------------------------

        task = understand(
            user_input
        )


        # -----------------------------------------
        # Execute requested action
        # -----------------------------------------

        result = execute(
            task
        )


        # -----------------------------------------
        # Store pending operation
        # -----------------------------------------

        if (
            result
            and result.get("status")
            in {
                "confirmation_required",
                "selection_required",
                "close_confirmation_required",
                "web_fallback_confirmation_required"
            }
        ):

            pending_action = result


        # -----------------------------------------
        # Exit
        # -----------------------------------------

        if (
            task.intent == "exit"
            or task.data.get("action") == "exit"
        ):

            break


        # -----------------------------------------
        # Conversation handling
        # -----------------------------------------

        conversation = (
            task.data.get("conversation")
            if task.data
            else None
        )


        # Pure conversation
        #
        # Example:
        # "Hey bro, what's up?"
        #
        # task.intent = conversation
        # conversation = None
        #
        # In this case send the original message.
        # -----------------------------------------

        if task.intent == "conversation":

            conversation = user_input


        # -----------------------------------------
        # Compound / action + conversation
        #
        # Example:
        # "Open YouTube and who is the best
        #  Bedwars player?"
        #
        # The action has already been executed.
        # Now let Drax respond to the conversational
        # portion naturally.
        # -----------------------------------------

        if conversation:

            response = companion.chat(
                conversation,
                execution=result
            )

            if response:

                safe_print(
                    f"\n🤖 {response}"
                )