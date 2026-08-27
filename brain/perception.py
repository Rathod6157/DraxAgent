import time
from pathlib import Path

from desktop_controller import desktop


class DesktopPerception:
    """
    Drax's desktop perception layer.

    Collects:
        - screen dimensions
        - mouse position
        - screenshot

    This is the foundation for future visual understanding.
    """

    def __init__(self, controller=None, memory_dir="memory"):
        self.controller = controller or desktop
        self.memory_dir = Path(memory_dir)

        self.memory_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # ============================================================
    # SCREEN SIZE
    # ============================================================

    def get_screen_size(self):
        """
        Get the current desktop resolution.

        IMPORTANT:
        screen_size is a controller method, not necessarily
        a primitive desktop action.
        """

        try:
            return self.controller.screen_size()

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    def screen_size(self):
        """
        Backwards-compatible alias for get_screen_size().
        """
        return self.get_screen_size()

    # ============================================================
    # MOUSE POSITION
    # ============================================================

    def get_mouse_position(self):

        try:
            return self.controller.mouse_position()

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    def mouse_position(self):
        """
        Backwards-compatible alias for get_mouse_position().
        """
        return self.get_mouse_position()

    # ============================================================
    # SCREENSHOT
    # ============================================================

    def capture_screenshot(self, filename=None):

        if filename is None:
            filename = (
                f"observation_{int(time.time() * 1000)}.png"
            )

        path = self.memory_dir / filename

        try:
            return self.controller.screenshot(str(path))

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ============================================================
    # FULL OBSERVATION
    # ============================================================

    def observe(self, filename=None):

        screen = self.get_screen_size()
        mouse = self.get_mouse_position()
        screenshot = self.capture_screenshot(filename)

        success = (
            screen.get("success", False)
            and mouse.get("success", False)
            and screenshot.get("success", False)
        )

        return {
            "success": success,
            "observation": {
                "screen": screen,
                "mouse": mouse,
                "screenshot": screenshot,
            }
        }

    # ============================================================
    # WATCH DESKTOP
    # ============================================================

    def watch(
        self,
        duration=5,
        interval=1.0,
    ):
        """
        Continuously observe the desktop.

        Returns a list of observations.
        """

        observations = []

        start = time.time()

        while time.time() - start < duration:

            observation = self.observe()

            observations.append(observation)

            time.sleep(interval)

        return {
            "success": True,
            "duration": duration,
            "count": len(observations),
            "observations": observations,
        }


# ================================================================
# SHARED PERCEPTION ENGINE
# ================================================================

perception = DesktopPerception()