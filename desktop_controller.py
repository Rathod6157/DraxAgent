import os
import time
import webbrowser
import subprocess
from pathlib import Path

import pyautogui


# ============================================================
# Drax Desktop Controller
# ============================================================
#
# This is deliberately a LOW-LEVEL layer.
#
# Drax's intelligence will eventually decide:
#
#     "What should I do next?"
#
# This module only knows:
#
#     "How do I physically do it?"
#
# ============================================================


pyautogui.PAUSE = 0.15
pyautogui.FAILSAFE = True


class DesktopController:
    """
    Low-level computer control for DraxAgent.
    """

    # --------------------------------------------------------
    # WAIT
    # --------------------------------------------------------

    def wait(self, seconds=1.0):
        """
        Wait for the desktop/application to react.
        """

        seconds = float(seconds)

        if seconds < 0:
            seconds = 0

        time.sleep(seconds)

        return {
            "success": True,
            "action": "wait",
            "seconds": seconds,
        }


    # --------------------------------------------------------
    # OPEN URL
    # --------------------------------------------------------

    def open_url(self, url):
        """
        Open a URL in the system's default browser.
        """

        url = str(url).strip()

        if not url:
            return {
                "success": False,
                "error": "No URL supplied.",
            }

        try:

            webbrowser.open(url)

            return {
                "success": True,
                "action": "open_url",
                "target": url,
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }


    # --------------------------------------------------------
    # OPEN APPLICATION
    # --------------------------------------------------------

    def open_app(self, application):
        """
        Ask Windows to launch an application.

        Examples:

            chrome
            notepad
            calc
            vscode
        """

        application = str(application).strip()

        if not application:
            return {
                "success": False,
                "error": "No application supplied.",
            }

        try:

            # Windows "start" command.
            #
            # This allows Windows to resolve applications
            # registered with the system.

            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    "start",
                    "",
                    application,
                ],
                shell=False,
            )

            return {
                "success": True,
                "action": "open_app",
                "target": application,
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }


    # --------------------------------------------------------
    # CLICK
    # --------------------------------------------------------

    def click(self, x=None, y=None, button="left", clicks=1):
        """
        Click the mouse.

        Coordinates are optional.

        If x/y are omitted, Drax clicks the current
        mouse position.
        """

        try:

            if x is None or y is None:

                pyautogui.click(
                    button=button,
                    clicks=int(clicks),
                )

            else:

                pyautogui.click(
                    x=int(x),
                    y=int(y),
                    button=button,
                    clicks=int(clicks),
                )

            return {
                "success": True,
                "action": "click",
                "x": x,
                "y": y,
                "button": button,
                "clicks": clicks,
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }


    # --------------------------------------------------------
    # MOVE MOUSE
    # --------------------------------------------------------

    def move_mouse(self, x, y, duration=0.2):
        """
        Move the mouse cursor.
        """

        try:

            pyautogui.moveTo(
                int(x),
                int(y),
                duration=float(duration),
            )

            return {
                "success": True,
                "action": "move_mouse",
                "x": int(x),
                "y": int(y),
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }


    # --------------------------------------------------------
    # TYPE TEXT
    # --------------------------------------------------------

    def type_text(self, text, interval=0.02):
        """
        Type text into the currently focused application.
        """

        text = str(text)

        try:

            pyautogui.write(
                text,
                interval=float(interval),
            )

            return {
                "success": True,
                "action": "type",
                "text": text,
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }


    # --------------------------------------------------------
    # PRESS KEY
    # --------------------------------------------------------

    def press(self, key):
        """
        Press a keyboard key.

        Examples:

            enter
            esc
            tab
            space
            backspace
            up
            down
        """

        key = str(key).strip().lower()

        if not key:
            return {
                "success": False,
                "error": "No key supplied.",
            }

        try:

            pyautogui.press(key)

            return {
                "success": True,
                "action": "press",
                "key": key,
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }


    # --------------------------------------------------------
    # HOTKEY
    # --------------------------------------------------------

    def hotkey(self, *keys):
        """
        Press a keyboard combination.

        Example:

            hotkey("ctrl", "l")

        """

        if not keys:
            return {
                "success": False,
                "error": "No keys supplied.",
            }

        try:

            pyautogui.hotkey(
                *[
                    str(key).strip().lower()
                    for key in keys
                ]
            )

            return {
                "success": True,
                "action": "hotkey",
                "keys": list(keys),
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }


    # --------------------------------------------------------
    # SCROLL
    # --------------------------------------------------------

    def scroll(self, amount):
        """
        Scroll vertically.

        Positive = up
        Negative = down
        """

        try:

            amount = int(amount)

            pyautogui.scroll(amount)

            return {
                "success": True,
                "action": "scroll",
                "amount": amount,
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }


    # --------------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------------

    def screenshot(self, path="memory/drax_screen.png"):
        """
        Capture the current screen.

        This will eventually become the input to Drax's
        visual reasoning system.
        """

        try:

            output = Path(path)

            output.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            image = pyautogui.screenshot()

            image.save(output)

            return {
                "success": True,
                "action": "screenshot",
                "path": str(output),
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }

    def screen_size(self):
        """
        Return the current screen dimensions.
        """

        try:
            import pyautogui

            width, height = pyautogui.size()

            return {
                "success": True,
                "action": "screen_size",
                "width": width,
                "height": height,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    # --------------------------------------------------------
    # MOUSE POSITION
    # --------------------------------------------------------

    def mouse_position(self):
        """
        Return the current mouse coordinates.
        """

        try:

            x, y = pyautogui.position()

            return {
                "success": True,
                "action": "mouse_position",
                "x": x,
                "y": y,
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }


    # --------------------------------------------------------
    # GENERIC ACTION DISPATCHER
    # --------------------------------------------------------

    def execute(self, action):
        """
        Execute an action dictionary.

        Example:

            {
                "type": "open_url",
                "url": "https://youtube.com"
            }

        """

        if not isinstance(action, dict):

            return {
                "success": False,
                "error": "Action must be a dictionary.",
            }


        action_type = (
            action.get("type")
            or action.get("action")
            or ""
        ).strip().lower()


        if not action_type:

            return {
                "success": False,
                "error": "Action has no type.",
            }


        # ----------------------------------------------------
        # OPEN URL
        # ----------------------------------------------------

        if action_type == "open_url":

            return self.open_url(
                action.get("url")
                or action.get("target")
                or ""
            )


        # ----------------------------------------------------
        # OPEN APPLICATION
        # ----------------------------------------------------

        if action_type == "open_app":

            return self.open_app(
                action.get("application")
                or action.get("app")
                or action.get("target")
                or ""
            )


        # ----------------------------------------------------
        # CLICK
        # ----------------------------------------------------

        if action_type == "click":

            return self.click(
                x=action.get("x"),
                y=action.get("y"),
                button=action.get(
                    "button",
                    "left",
                ),
                clicks=action.get(
                    "clicks",
                    1,
                ),
            )


        # ----------------------------------------------------
        # MOVE MOUSE
        # ----------------------------------------------------

        if action_type == "move_mouse":

            return self.move_mouse(
                x=action.get("x"),
                y=action.get("y"),
                duration=action.get(
                    "duration",
                    0.2,
                ),
            )


        # ----------------------------------------------------
        # TYPE
        # ----------------------------------------------------

        if action_type == "type":

            return self.type_text(
                text=action.get(
                    "text",
                    "",
                ),
                interval=action.get(
                    "interval",
                    0.02,
                ),
            )


        # ----------------------------------------------------
        # PRESS
        # ----------------------------------------------------

        if action_type == "press":

            return self.press(
                action.get(
                    "key",
                    "",
                )
            )


        # ----------------------------------------------------
        # HOTKEY
        # ----------------------------------------------------

        if action_type == "hotkey":

            keys = action.get(
                "keys",
                [],
            )

            if not isinstance(keys, list):

                return {
                    "success": False,
                    "error": "Hotkey keys must be a list.",
                }

            return self.hotkey(
                *keys
            )


        # ----------------------------------------------------
        # SCROLL
        # ----------------------------------------------------

        if action_type == "scroll":

            return self.scroll(
                action.get(
                    "amount",
                    0,
                )
            )


        # ----------------------------------------------------
        # WAIT
        # ----------------------------------------------------

        if action_type == "wait":

            return self.wait(
                action.get(
                    "seconds",
                    1,
                )
            )


        # ----------------------------------------------------
        # SCREENSHOT
        # ----------------------------------------------------

        if action_type == "screenshot":

            return self.screenshot(
                action.get(
                    "path",
                    "memory/drax_screen.png",
                )
            )


        # ----------------------------------------------------
        # MOUSE POSITION
        # ----------------------------------------------------

        if action_type == "mouse_position":

            return self.mouse_position()


        # ----------------------------------------------------
        # UNKNOWN ACTION
        # ----------------------------------------------------

        return {
            "success": False,
            "error": (
                f"Unknown desktop action: "
                f"{action_type}"
            ),
        }


# ============================================================
# SINGLE SHARED CONTROLLER
# ============================================================

desktop = DesktopController()