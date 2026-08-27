from time import sleep

from desktop_controller import desktop
from .screen_vision import vision


class VisualAutomation:
    """
    Vision-guided desktop automation for Drax.

    Drax observes the screen, asks Gemini what is visible,
    then uses the returned coordinates to interact with it.
    """

    def __init__(self, controller=None, vision_engine=None):
        self.controller = controller or desktop
        self.vision = vision_engine or vision

    # ============================================================
    # OBSERVE
    # ============================================================

    def observe(self, instruction=None):
        """
        Capture the current desktop and analyze it with Gemini.
        """

        screenshot = self.controller.screenshot(
            "memory/drax_observation.png"
        )

        if not screenshot.get("success", False):
            return {
                "success": False,
                "error": "Could not capture desktop screenshot.",
                "screenshot": screenshot,
            }

        image_path = screenshot.get("path")

        if not image_path:
            return {
                "success": False,
                "error": "Screenshot path was not returned.",
            }

        result = self.vision.analyze(
            image_path,
            instruction=instruction,
        )

        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get(
                    "error",
                    "Vision analysis failed."
                ),
                "screenshot": screenshot,
            }

        return {
            "success": True,
            "screenshot": screenshot,
            "vision": result["vision"],
        }

    # ============================================================
    # FIND ELEMENT
    # ============================================================

    @staticmethod
    def find_element(vision_data, target):
        """
        Find a visible element by its label.

        Matching is intentionally simple for now.
        """

        if not isinstance(vision_data, dict):
            return None

        elements = vision_data.get("elements", [])

        target = target.lower().strip()

        for element in elements:

            label = str(
                element.get("label", "")
            ).lower().strip()

            if target == label:
                return element

        # Fallback: partial match

        for element in elements:

            label = str(
                element.get("label", "")
            ).lower().strip()

            if target in label or label in target:
                return element

        return None

    # ============================================================
    # CLICK ELEMENT
    # ============================================================

    def click_element(self, element):
        """
        Click the center of a vision-detected element.
        """

        if not isinstance(element, dict):
            return {
                "success": False,
                "error": "Invalid visual element."
            }

        try:
            x = int(element["x"])
            y = int(element["y"])
            width = int(element.get("width", 0))
            height = int(element.get("height", 0))

        except (KeyError, TypeError, ValueError):
            return {
                "success": False,
                "error": "Visual element has invalid coordinates."
            }

        # If Gemini supplied a bounding box,
        # click its center rather than its top-left corner.

        center_x = x + (width // 2)
        center_y = y + (height // 2)

        return self.controller.execute({
            "type": "click",
            "x": center_x,
            "y": center_y,
        })

    # ============================================================
    # CLICK BY LABEL
    # ============================================================

    def click_by_label(
        self,
        target,
        instruction=None,
        retry=True,
        retry_delay=0.5,
    ):
        """
        Observe the screen and click a visible element by label.
        """

        observation = self.observe(
            instruction=instruction
        )

        if not observation.get("success", False):
            return observation

        element = self.find_element(
            observation["vision"],
            target,
        )

        if element:

            result = self.click_element(element)

            return {
                "success": result.get("success", False),
                "target": target,
                "element": element,
                "result": result,
                "vision": observation["vision"],
            }

        # --------------------------------------------------------
        # Optional second observation
        # --------------------------------------------------------

        if retry:

            sleep(retry_delay)

            observation = self.observe(
                instruction=instruction
            )

            if observation.get("success", False):

                element = self.find_element(
                    observation["vision"],
                    target,
                )

                if element:

                    result = self.click_element(
                        element
                    )

                    return {
                        "success": result.get(
                            "success", False
                        ),
                        "target": target,
                        "element": element,
                        "result": result,
                        "vision": observation["vision"],
                    }

        return {
            "success": False,
            "error": (
                f"Could not find '{target}' "
                "on the current screen."
            ),
            "vision": observation.get(
                "vision"
            ),
        }


# ================================================================
# SHARED INSTANCE
# ================================================================

visual = VisualAutomation()