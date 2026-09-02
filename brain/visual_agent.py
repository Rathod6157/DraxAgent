from time import sleep

from .perception import perception
from .screen_vision import vision
from .desktop_automation import automation


class VisualAgent:
    """
    Drax's closed-loop visual computer-use agent.

    Observe → Understand → Find → Act → Verify

    Vision coordinates are expected to be normalized to 0–1000
    when the vision model reports normalized_1000 mode.
    """

    def __init__(
        self,
        max_steps=10,
        observation_path="memory/drax_observation.png",
        verify_delay=0.5,
    ):
        self.max_steps = max_steps
        self.observation_path = observation_path
        self.verify_delay = verify_delay

    # ============================================================
    # OBSERVE
    # ============================================================

    def observe(self, instruction=None, filename=None):
        """
        Capture the desktop and ask the vision system to understand it.
        """

        observation = perception.observe(filename)

        if not observation.get("success", False):
            return {
                "success": False,
                "stage": "perception",
                "error": observation.get(
                    "error",
                    "Perception failed.",
                ),
            }

        inner = observation.get("observation", {})

        screenshot = inner.get("screenshot")

        if not screenshot:
            screenshot = observation.get("screenshot")

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

        result = vision.analyze(
            screenshot_path,
            instruction=instruction or (
                "Understand the current desktop for Drax. "
                "Identify the visible application, important text, "
                "interactive UI elements, and useful possible actions. "
                "Return accurate coordinates for interactive elements."
            ),
        )

        if not result.get("success", False):
            return {
                "success": False,
                "stage": "vision",
                "error": result.get(
                    "error",
                    "Vision analysis failed.",
                ),
                "screenshot": screenshot_path,
            }

        return {
            "success": True,
            "screenshot": screenshot_path,
            "vision": result["vision"],
        }

    # ============================================================
    # FIND ELEMENT
    # ============================================================

    def find_element(self, vision_data, target):
        """
        Find the best matching visible element.

        Matching order:
            1. exact label
            2. case-insensitive partial match
        """

        if not isinstance(vision_data, dict):
            return None

        elements = vision_data.get("elements", [])

        if not isinstance(elements, list):
            return None

        target = str(target).lower().strip()

        # Exact match
        for element in elements:
            label = str(
                element.get("label", "")
            ).lower().strip()

            if label == target:
                return element

        # Partial match
        for element in elements:
            label = str(
                element.get("label", "")
            ).lower().strip()

            if target in label or label in target:
                return element

        return None

    # ============================================================
    # COORDINATE CONVERSION
    # ============================================================

    def _get_screen_size(self):
        """
        Get the real physical screen size.
        """

        result = perception.get_screen_size()

        if not result.get("success", False):
            raise RuntimeError(
                result.get(
                    "error",
                    "Could not determine screen size.",
                )
            )

        return (
            int(result["width"]),
            int(result["height"]),
        )

    def _element_center(self, element, vision_data):
        """
        Convert vision coordinates into physical screen pixels.

        Supported coordinate modes:

            normalized_1000
                0–1000 coordinate system.

            screen_pixels
                Coordinates already expressed in pixels.

        The normalized_1000 mode is the preferred contract.
        """

        try:
            x = float(element["x"])
            y = float(element["y"])
            width = float(element.get("width", 0))
            height = float(element.get("height", 0))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                "Invalid element coordinates."
            ) from exc

        center_x = x + width / 2
        center_y = y + height / 2

        coordinate_mode = vision_data.get(
            "coordinate_mode",
            "normalized_1000",
        )

        if coordinate_mode == "normalized_1000":

            screen_width, screen_height = self._get_screen_size()

            physical_x = (
                center_x / 1000.0
            ) * screen_width

            physical_y = (
                center_y / 1000.0
            ) * screen_height

        elif coordinate_mode == "screen_pixels":

            physical_x = center_x
            physical_y = center_y

        else:
            raise ValueError(
                f"Unsupported vision coordinate mode: "
                f"{coordinate_mode}"
            )

        return (
            int(round(physical_x)),
            int(round(physical_y)),
        )

    # ============================================================
    # CLICK ELEMENT
    # ============================================================

    def click_element(self, element, vision_data):
        """
        Click the center of a vision-detected element.
        """

        if not element:
            return {
                "success": False,
                "error": "Element not found.",
            }

        try:
            screen_width, screen_height = self._get_screen_size()

            click_x, click_y = self._element_center(
                element,
                vision_data,
            )

            # Safety boundary check.
            if not (
                0 <= click_x < screen_width
                and 0 <= click_y < screen_height
            ):
                return {
                    "success": False,
                    "error": (
                        "Calculated click position is outside "
                        "the physical screen."
                    ),
                    "x": click_x,
                    "y": click_y,
                    "screen": {
                        "width": screen_width,
                        "height": screen_height,
                    },
                }

            print()
            print("Vision coordinates:")
            print(
                f"  x={element.get('x')}, "
                f"y={element.get('y')}, "
                f"width={element.get('width')}, "
                f"height={element.get('height')}"
            )

            print(
                "Vision coordinate mode:",
                vision_data.get(
                    "coordinate_mode",
                    "normalized_1000",
                ),
            )

            print()
            print("Real screen:")
            print(
                f"  width={screen_width}, "
                f"height={screen_height}"
            )

            print()
            print(
                f"Vision center: "
                f"({element.get('x', 0) + element.get('width', 0) / 2}, "
                f"{element.get('y', 0) + element.get('height', 0) / 2})"
            )

            print(
                f"Final physical click: "
                f"({click_x}, {click_y})"
            )

            return automation.execute_action({
                "type": "click",
                "x": click_x,
                "y": click_y,
            })

        except (ValueError, RuntimeError) as exc:
            return {
                "success": False,
                "error": str(exc),
            }

    # ============================================================
    # CLICK BY DESCRIPTION
    # ============================================================

    def click(self, target):
        """
        Observe the desktop, locate a target, click it,
        and return the complete action context.
        """

        observation = self.observe(
            instruction=(
                "Find the visible desktop UI element named or "
                "described as: "
                f"{target}. "
                "Return its bounding box accurately."
            )
        )

        if not observation.get("success", False):
            return observation

        vision_data = observation["vision"]

        element = self.find_element(
            vision_data,
            target,
        )

        if not element:
            return {
                "success": False,
                "stage": "search",
                "error": (
                    f"Could not find visible element: {target}"
                ),
                "vision": vision_data,
            }

        click_result = self.click_element(
            element,
            vision_data,
        )

        return {
            "success": click_result.get("success", False),
            "target": target,
            "element": element,
            "click": click_result,
            "vision": vision_data,
        }

    # ============================================================
    # TYPE TEXT
    # ============================================================

    def type_text(self, text):
        """
        Type text using the existing desktop automation layer.
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

    def hotkey(self, *keys):
        """
        Press a keyboard shortcut.

        Example:
            agent.hotkey("ctrl", "l")
        """

        if not keys:
            return {
                "success": False,
                "error": "At least one key is required.",
            }

        return automation.execute_action({
            "type": "hotkey",
            "keys": list(keys),
        })

    # ============================================================
    # VERIFY
    # ============================================================

    def verify(self, instruction=None):
        """
        Re-observe the desktop after an action.

        This is deliberately a fresh perception cycle.
        """

        return self.observe(
            instruction=instruction or (
                "Verify the result of the previous action. "
                "Describe the current desktop state and identify "
                "what changed. Pay particular attention to whether "
                "the requested UI action actually succeeded."
            )
        )

    # ============================================================
    # CLICK + VERIFY
    # ============================================================

    def click_and_verify(self, target):
        """
        Complete closed-loop interaction:

            Observe
            Find
            Click
            Observe again
            Verify
        """

        result = self.click(target)

        if not result.get("success", False):
            return result

        sleep(self.verify_delay)

        verification = self.verify(
            instruction=(
                f"Verify whether the requested action to click "
                f"'{target}' succeeded. "
                f"Look for visible UI changes, selection state, "
                f"opened panels, dialogs, or other evidence."
            )
        )

        return {
            "success": verification.get("success", False),
            "target": target,
            "action": result,
            "verification": verification,
        }

    # ============================================================
    # OBSERVE ONLY
    # ============================================================

    def describe_screen(self):
        """
        Understand the current desktop without performing an action.

        This is the foundation for commands such as:

            "Drax, what's on my screen?"
            "Drax, what am I looking at?"
        """

        return self.observe(
            instruction=(
                "Describe the current desktop clearly and concisely. "
                "Identify the main visible application, important "
                "windows or panels, visible text, and what the user "
                "appears to be doing. Do not perform any action."
            )
        )

    # ============================================================
    # EXECUTE SIMPLE ACTION
    # ============================================================

    def execute_action(self, action):
        """
        Execute one visual-agent action.

        Supported actions:

            click
            type
            press
            hotkey
            observe
        """

        if not isinstance(action, dict):
            return {
                "success": False,
                "error": "Action must be a dictionary.",
            }

        action_type = action.get("type")

        if action_type == "click":

            target = action.get("target")

            if not target:
                return {
                    "success": False,
                    "error": (
                        "Visual click requires a target."
                    ),
                }

            return self.click_and_verify(target)

        if action_type == "type":

            result = self.type_text(
                action.get("text", "")
            )

            return {
                "success": result.get("success", False),
                "action": result,
            }

        if action_type == "press":

            result = self.press(
                action.get("key")
            )

            return {
                "success": result.get("success", False),
                "action": result,
            }

        if action_type == "hotkey":

            keys = action.get("keys", [])

            if not isinstance(keys, list):
                return {
                    "success": False,
                    "error": "Hotkey keys must be a list.",
                }

            result = self.hotkey(*keys)

            return {
                "success": result.get("success", False),
                "action": result,
            }

        if action_type == "observe":

            return self.describe_screen()

        return {
            "success": False,
            "error": (
                f"Unsupported visual action: {action_type}"
            ),
        }

    # ============================================================
    # RUN
    # ============================================================

    def run(self, instruction, target=None):
        """
        Execute a simple visual task.

        If target is supplied:

            Observe → Find → Click → Verify

        If no target is supplied, return an observation and
        explain that higher-level planning is not yet connected.
        """

        print()
        print("===== DRAX VISUAL AGENT =====")
        print()
        print("Instruction:", instruction)

        if target:

            print()
            print("Observing desktop...")

            result = self.click_and_verify(target)

            return {
                "success": result.get("success", False),
                "instruction": instruction,
                "target": target,
                "action": result.get("action"),
                "verification": result.get(
                    "verification"
                ),
            }

        observation = self.describe_screen()

        return {
            "success": observation.get("success", False),
            "instruction": instruction,
            "observation": observation,
            "message": (
                "Visual observation completed. "
                "Higher-level task planning is not yet "
                "connected to the visual agent."
            ),
        }


# ================================================================
# SHARED AGENT
# ================================================================

visual_agent = VisualAgent()