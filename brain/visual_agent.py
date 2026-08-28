from time import sleep

from .perception import perception
from .screen_vision import vision
from .desktop_automation import automation


class VisualAgent:
    """
    Drax's closed-loop visual computer-use agent.

    Flow:

        Observe
          ↓
        Understand
          ↓
        Find target
          ↓
        Convert coordinates
          ↓
        Act
          ↓
        Verify
    """

    def __init__(
        self,
        max_steps=10,
        observation_path="memory/drax_observation.png",
    ):
        self.max_steps = max_steps
        self.observation_path = observation_path

    # ============================================================
    # OBSERVE
    # ============================================================

    def observe(self, instruction=None):
        """
        Capture the desktop and analyze it with Drax vision.
        """

        observation = perception.observe()

        if not observation.get("success", False):
            return {
                "success": False,
                "stage": "perception",
                "error": observation.get(
                    "error",
                    "Perception failed.",
                ),
            }

        inner = observation.get(
            "observation",
            {},
        )

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
                "Identify visible applications, UI elements, "
                "buttons, inputs, links, menus, and useful "
                "interactive elements."
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
        """

        elements = vision_data.get(
            "elements",
            [],
        )

        if not isinstance(elements, list):
            return None

        target = str(target).lower().strip()

        # --------------------------------------------------------
        # Exact match
        # --------------------------------------------------------

        for element in elements:

            label = str(
                element.get(
                    "label",
                    "",
                )
            ).lower().strip()

            if label == target:
                return element

        # --------------------------------------------------------
        # Partial match
        # --------------------------------------------------------

        for element in elements:

            label = str(
                element.get(
                    "label",
                    "",
                )
            ).lower().strip()

            if (
                target in label
                or label in target
            ):
                return element

        return None

    # ============================================================
    # REAL SCREEN SIZE
    # ============================================================

    def _get_screen_size(self):
        """
        Get the actual physical screen dimensions.
        """

        result = perception.screen_size()

        if not result.get("success", False):
            return None

        width = result.get("width")
        height = result.get("height")

        if not width or not height:
            return None

        return int(width), int(height)

    # ============================================================
    # NORMALIZED COORDINATE CONVERSION
    # ============================================================

    def _normalized_to_screen(
        self,
        x,
        y,
        width,
        height,
    ):
        """
        Convert Drax vision coordinates from the
        normalized 0-1000 coordinate system into
        physical screen pixels.

        Vision coordinate system:

            (0,0) ----------------> (1000,0)
              |
              |
              |
              v
           (0,1000)
        """

        screen = self._get_screen_size()

        if not screen:
            return None

        screen_width, screen_height = screen

        # --------------------------------------------------------
        # Center of bounding box in normalized coordinates
        # --------------------------------------------------------

        center_x = x + (width / 2.0)
        center_y = y + (height / 2.0)

        # --------------------------------------------------------
        # Convert 0-1000 → physical screen pixels
        # --------------------------------------------------------

        physical_x = (
            center_x / 1000.0
        ) * screen_width

        physical_y = (
            center_y / 1000.0
        ) * screen_height

        physical_x = int(round(physical_x))
        physical_y = int(round(physical_y))

        # --------------------------------------------------------
        # Safety clamp
        # --------------------------------------------------------

        physical_x = max(
            0,
            min(
                physical_x,
                screen_width - 1,
            ),
        )

        physical_y = max(
            0,
            min(
                physical_y,
                screen_height - 1,
            ),
        )

        return {
            "x": physical_x,
            "y": physical_y,
            "screen_width": screen_width,
            "screen_height": screen_height,
            "vision_center_x": center_x,
            "vision_center_y": center_y,
            "coordinate_mode": "normalized_1000",
        }

    # ============================================================
    # CLICK ELEMENT
    # ============================================================

    def click_element(self, element):
        """
        Click the center of a vision-detected element.

        IMPORTANT:

        Vision coordinates are ALWAYS interpreted as
        normalized 0-1000 coordinates.

        They are converted into physical screen pixels
        before being passed to desktop automation.
        """

        if not element:
            return {
                "success": False,
                "error": "Element not found.",
            }

        try:
            x = float(element["x"])
            y = float(element["y"])
            width = float(
                element.get(
                    "width",
                    0,
                )
            )
            height = float(
                element.get(
                    "height",
                    0,
                )
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):

            return {
                "success": False,
                "error": "Invalid element coordinates.",
            }

        # --------------------------------------------------------
        # Validate normalized coordinates
        # --------------------------------------------------------

        if not (
            0 <= x <= 1000
            and 0 <= y <= 1000
        ):
            return {
                "success": False,
                "error": (
                    "Vision coordinates are outside "
                    "the normalized 0-1000 range."
                ),
                "element": element,
            }

        if width < 0 or height < 0:
            return {
                "success": False,
                "error": "Element width/height cannot be negative.",
                "element": element,
            }

        # --------------------------------------------------------
        # Convert to real screen coordinates
        # --------------------------------------------------------

        converted = self._normalized_to_screen(
            x,
            y,
            width,
            height,
        )

        if not converted:
            return {
                "success": False,
                "error": "Could not determine physical screen size.",
                "element": element,
            }

        click_x = converted["x"]
        click_y = converted["y"]

        print()
        print("Vision coordinates:")
        print(
            f"  x={x}, y={y}, "
            f"width={width}, height={height}"
        )

        print(
            "Vision coordinate mode: "
            "normalized_1000"
        )

        print()
        print("Real screen:")
        print(
            f"  width={converted['screen_width']}, "
            f"height={converted['screen_height']}"
        )

        print()
        print(
            "Vision center:"
            f" ({converted['vision_center_x']:.1f}, "
            f"{converted['vision_center_y']:.1f})"
        )

        print(
            "Final physical click:"
            f" ({click_x}, {click_y})"
        )

        # --------------------------------------------------------
        # Execute physical click
        # --------------------------------------------------------

        click_result = automation.execute_action({
            "type": "click",
            "x": click_x,
            "y": click_y,
        })

        return click_result

    # ============================================================
    # CLICK BY DESCRIPTION
    # ============================================================

    def click(self, target):
        """
        Observe the screen, find a target, and click it.
        """

        observation = self.observe(
            instruction=(
                "Find the visible desktop element named "
                "or described as: "
                + str(target)
                + ". "
                "Return its bounding box using the required "
                "normalized 0-1000 coordinate system."
            )
        )

        if not observation.get(
            "success",
            False,
        ):
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
                    f"Could not find visible element: "
                    f"{target}"
                ),
                "vision": vision_data,
            }

        click_result = self.click_element(
            element
        )

        return {
            "success": click_result.get(
                "success",
                False,
            ),
            "target": target,
            "element": element,
            "click": click_result,
            "vision": vision_data,
        }

    # ============================================================
    # VERIFY ACTION
    # ============================================================

    def verify_action(
        self,
        target,
        instruction,
    ):
        """
        Observe the desktop after an action and ask
        the vision system whether the requested target
        appears to be active/selected/opened.

        This does NOT assume that a successful physical
        click means the task succeeded.
        """

        verification = self.observe(
            instruction=(
                "Verify the result of the previous action. "
                f"The requested target was: {target}. "
                "Determine whether that target was actually "
                "activated, selected, opened, focused, or "
                "otherwise changed state. "
                "Do NOT assume success merely because a click "
                "was performed. "
                "Pay special attention to visual indicators "
                "such as highlighted tabs, opened panels, "
                "focus indicators, changed content, or "
                "selection state."
            )
        )

        if not verification.get(
            "success",
            False,
        ):
            return verification

        return verification

    # ============================================================
    # RUN SIMPLE VISUAL TASK
    # ============================================================

    def run(
        self,
        instruction,
        target=None,
    ):
        """
        Execute a simple visual task.

        Example:

            agent.run(
                "Find the Terminal tab and click it.",
                target="Terminal"
            )
        """

        print()
        print(
            "===== DRAX VISUAL AGENT ====="
        )
        print()
        print(
            "Instruction:",
            instruction,
        )

        if not target:
            return {
                "success": False,
                "error": (
                    "No target was supplied. "
                    "Complex task planning is not implemented yet."
                ),
            }

        # --------------------------------------------------------
        # OBSERVE + FIND + CLICK
        # --------------------------------------------------------

        print()
        print("Observing desktop...")

        result = self.click(target)

        if not result.get(
            "success",
            False,
        ):
            return result

        print()
        print(
            "Target found:",
            result["element"],
        )

        print()
        print(
            "Click result:",
            result["click"],
        )

        # --------------------------------------------------------
        # Give the UI time to react
        # --------------------------------------------------------

        sleep(0.7)

        # --------------------------------------------------------
        # VERIFY
        # --------------------------------------------------------

        print()
        print("Verifying result...")

        verification = self.verify_action(
            target,
            instruction,
        )

        # --------------------------------------------------------
        # IMPORTANT:
        #
        # Observation succeeding only means that Drax was able
        # to observe the screen.
        #
        # We expose verification separately instead of falsely
        # claiming the click succeeded.
        # --------------------------------------------------------

        return {
            "success": (
                result.get("success", False)
                and verification.get(
                    "success",
                    False,
                )
            ),
            "instruction": instruction,
            "target": target,
            "action": result,
            "verification": verification,
        }


# ================================================================
# SHARED AGENT
# ================================================================

visual_agent = VisualAgent()