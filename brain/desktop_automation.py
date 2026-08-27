from time import sleep

from desktop_controller import desktop

from brain.perception import perception

class DesktopAutomation:
    """
    High-level desktop automation engine for Drax.

    The planner decides WHAT should happen.
    This class decides HOW to execute it.
    """

    def __init__(self, controller=None):
        self.controller = controller or desktop

    # ============================================================
    # EXECUTE ONE ACTION
    # ============================================================

    def execute_action(self, action):

        if not isinstance(action, dict):
            return {
                "success": False,
                "error": "Action must be a dictionary."
            }

        action_type = action.get("type")

        # --------------------------------------------------------
        # Semantic browser search
        # --------------------------------------------------------

        if action_type == "browser_search":

            query = action.get("query")

            if not query:
                return {
                    "success": False,
                    "error": "browser_search requires a query."
                }

            # Focus browser address/search navigation.
            result = self.controller.execute({
                "type": "hotkey",
                "keys": ["ctrl", "l"]
            })

            if not result.get("success", False):
                return result

            sleep(0.1)

            # Use the browser itself to perform the search.
            result = self.controller.execute({
                "type": "type",
                "text": query
            })

            if not result.get("success", False):
                return result

            sleep(0.05)

            return self.controller.execute({
                "type": "press",
                "key": "enter"
            })

        # --------------------------------------------------------
        # Normal primitive action
        # --------------------------------------------------------

        return self.controller.execute(action)

    # ============================================================
    # EXECUTE PLAN
    # ============================================================

    def execute_plan(
        self,
        actions,
        stop_on_failure=True,
        observe=False,
        delay=0.1,
    ):

        if not isinstance(actions, list):
            return {
                "success": False,
                "error": "Automation plan must be a list."
            }

        results = []

        for index, action in enumerate(actions, start=1):

            result = self.execute_action(action)

            results.append({
                "step": index,
                "action": action,
                "result": result,
            })

            if not result.get("success", False):

                if stop_on_failure:
                    return {
                        "success": False,
                        "failed_step": index,
                        "results": results,
                    }

            # Optional observation
            if observe:

                observation = self.observe(
                    f"automation_step_{index}.png"
                )

                results[-1]["observation"] = observation

            if delay > 0:
                sleep(delay)

        return {
            "success": True,
            "steps": len(actions),
            "results": results,
        }
        
    # ============================================================
    # OBSERVE DESKTOP
    # ============================================================

    def observe(self, filename="drax_observation.png"):
        """
        Capture the current desktop state.
        """

        return perception.observe(filename)


# ============================================================
# SHARED AUTOMATION ENGINE
# ============================================================

automation = DesktopAutomation()