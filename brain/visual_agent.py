from time import sleep

from .perception import perception
from .screen_vision import vision
from .desktop_automation import automation


class VisualAgent:
    """
    Drax's closed-loop visual computer-use agent.

    Observe → Understand → Locate → Act → Verify

    The vision model understands the screen.
    The automation layer performs the physical action.
    """

    def __init__(
        self,
        max_steps=10,
        observation_path="memory/drax_observation.png",
        min_confidence=0.70,
    ):
        self.max_steps = max_steps
        self.observation_path = observation_path
        self.min_confidence = min_confidence

    # ============================================================
    # OBSERVE
    # ============================================================

    def observe(self, instruction=None):
        """
        Capture the desktop and ask the vision model to understand it.
        """

        observation = perception.observe()

        if not observation.get("success", False):
            return {
                "success": False,
                "stage": "perception",
                "error": observation.get(
                    "error",
                    "Perception failed."
                ),
            }

        # --------------------------------------------------------
        # Get screenshot information
        # --------------------------------------------------------

        screenshot = observation.get("screenshot")

        if not screenshot:
            inner = observation.get("observation", {})
            screenshot = inner.get("screenshot")

        if not screenshot:
            return {
                "success": False,
                "stage": "perception",
                "error": "Perception did not return a screenshot.",
                "perception": observation,
            }

        screenshot_path = screenshot.get("path")

        if not screenshot_path:
            return {
                "success": False,
                "stage": "perception",
                "error": "Screenshot path was not returned.",
                "perception": observation,
            }

        # --------------------------------------------------------
        # Ask Gemini to understand screenshot
        # --------------------------------------------------------

        prompt = instruction or (
            "Understand the current desktop for Drax. "
            "Identify visible applications, windows, buttons, "
            "inputs, links, menus, dialogs, text, and other "
            "interactive elements. "
            "Return accurate bounding boxes and confidence values."
        )

        result = vision.analyze(
            screenshot_path,
            instruction=prompt,
        )

        if not result.get("success", False):
            return {
                "success": False,
                "stage": "vision",
                "error": result.get(
                    "error",
                    "Vision analysis failed."
                ),
                "screenshot": screenshot_path,
            }

        return {
            "success": True,
            "screenshot": screenshot_path,
            "vision": result.get("vision", {}),
        }

    # ============================================================
    # FIND ELEMENT
    # ============================================================

    def find_element(self, vision_data, target):
        """
        Find the best matching visible element.

        Matching order:
        1. Exact label
        2. Partial label
        3. Target contained in description
        """

        if not isinstance(vision_data, dict):
            return None

        elements = vision_data.get("elements", [])

        if not isinstance(elements, list):
            return None

        target = str(target).lower().strip()

        if not target:
            return None

        # --------------------------------------------------------
        # Exact match
        # --------------------------------------------------------

        for element in elements:

            label = str(
                element.get("label", "")
            ).lower().strip()

            if label == target:

                confidence = float(
                    element.get("confidence", 0)
                )

                if confidence >= self.min_confidence:
                    return element

        # --------------------------------------------------------
        # Partial match
        # --------------------------------------------------------

        candidates = []

        for element in elements:

            label = str(
                element.get("label", "")
            ).lower().strip()

            if not label:
                continue

            if target in label or label in target:

                confidence = float(
                    element.get("confidence", 0)
                )

                if confidence >= self.min_confidence:
                    candidates.append(
                        (confidence, element)
                    )

        if candidates:

            candidates.sort(
                key=lambda item: item[0],
                reverse=True,
            )

            return candidates[0][1]

        return None

    # ============================================================
    # CLICK ELEMENT
    # ============================================================

    def click_element(self, element):
        """
        Click the center of a detected bounding box.
        """

        if not element:
            return {
                "success": False,
                "error": "Element not found.",
            }

        try:
            x = int(element["x"])
            y = int(element["y"])
            width = int(element.get("width", 0))
            height = int(element.get("height", 0))

        except (KeyError, TypeError, ValueError):

            return {
                "success": False,
                "error": "Invalid element coordinates.",
            }

        # --------------------------------------------------------
        # Validate coordinates
        # --------------------------------------------------------

        if width < 0 or height < 0:
            return {
                "success": False,
                "error": "Invalid element dimensions.",
            }

        click_x = x + width // 2
        click_y = y + height // 2

        return automation.execute_action({
            "type": "click",
            "x": click_x,
            "y": click_y,
        })

    # ============================================================
    # TYPE TEXT
    # ============================================================

    def type_text(self, text):
        """
        Type text into the currently focused UI element.
        """

        if text is None:
            return {
                "success": False,
                "error": "Text cannot be None.",
            }

        return automation.execute_action({
            "type": "type",
            "text": str(text),
        })

    # ============================================================
    # PRESS KEY
    # ============================================================

    def press(self, key):
        """
        Press a keyboard key.
        """

        if not key:
            return {
                "success": False,
                "error": "Key is required.",
            }

        return automation.execute_action({
            "type": "press",
            "key": key,
        })

    # ============================================================
    # HOTKEY
    # ============================================================

    def hotkey(self, keys):
        """
        Execute a keyboard shortcut.
        """

        if not isinstance(keys, list) or not keys:
            return {
                "success": False,
                "error": "keys must be a non-empty list.",
            }

        return automation.execute_action({
            "type": "hotkey",
            "keys": keys,
        })

    # ============================================================
    # CLICK BY DESCRIPTION
    # ============================================================

    def click(self, target, retries=2):
        """
        Observe the screen, locate a target, and click it.

        Automatically retries observation if the target isn't
        immediately detected.
        """

        last_result = None

        for attempt in range(1, retries + 1):

            observation = self.observe(
                instruction=(
                    "Find the visible desktop element named or "
                    "described as: "
                    + str(target)
                    + ". "
                    "Return its exact visible bounding box."
                )
            )

            if not observation.get("success", False):
                last_result = observation
                sleep(0.3)
                continue

            vision_data = observation.get(
                "vision",
                {}
            )

            element = self.find_element(
                vision_data,
                target,
            )

            if element:

                click_result = self.click_element(
                    element
                )

                return {
                    "success": click_result.get(
                        "success",
                        False,
                    ),
                    "target": target,
                    "attempt": attempt,
                    "element": element,
                    "click": click_result,
                    "vision": vision_data,
                }

            last_result = {
                "success": False,
                "stage": "search",
                "error": (
                    f"Could not find visible element: "
                    f"{target}"
                ),
                "vision": vision_data,
                "attempt": attempt,
            }

            sleep(0.3)

        return last_result or {
            "success": False,
            "error": f"Could not find: {target}",
        }

    # ============================================================
    # VERIFY
    # ============================================================

    def verify(self, instruction):
        """
        Capture a fresh screenshot and ask Gemini to verify
        the current desktop state.
        """

        return self.observe(
            instruction=(
                instruction
                + "\n\n"
                "Compare the current state with the expected "
                "result of the previous action. "
                "Clearly state whether the action appears "
                "successful."
            )
        )

    # ============================================================
    # RUN CLICK TASK
    # ============================================================

    def run(self, instruction, target=None):
        """
        Execute a simple visual task.

        Example:

            visual_agent.run(
                "Click the Terminal tab.",
                target="Terminal"
            )
        """

        print()
        print("===== DRAX VISUAL AGENT =====")
        print()
        print("Instruction:", instruction)

        if not target:
            return {
                "success": False,
                "error": (
                    "No target supplied. "
                    "Advanced task planning is not implemented yet."
                ),
            }

        # --------------------------------------------------------
        # ACT
        # --------------------------------------------------------

        print()
        print("Observing desktop...")

        result = self.click(target)

        if not result.get("success", False):
            return {
                "success": False,
                "instruction": instruction,
                "target": target,
                "action": result,
            }

        print()
        print("Target found:", result["element"])

        print()
        print("Click result:", result["click"])

        # --------------------------------------------------------
        # Wait for UI reaction
        # --------------------------------------------------------

        sleep(0.7)

        # --------------------------------------------------------
        # VERIFY
        # --------------------------------------------------------

        print()
        print("Verifying result...")

        verification = self.verify(
            (
                "The agent attempted this action:\n"
                f"{instruction}\n\n"
                "Determine whether the action succeeded. "
                "Look for visible UI changes, active tabs, "
                "dialogs, selected controls, or other evidence."
            )
        )

        return {
            "success": verification.get(
                "success",
                False,
            ),
            "instruction": instruction,
            "target": target,
            "action": result,
            "verification": verification,
        }


# ============================================================
# SHARED AGENT
# ============================================================

visual_agent = VisualAgent()