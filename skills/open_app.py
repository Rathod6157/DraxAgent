import os
import subprocess
import winreg
import ctypes
from ctypes import wintypes

from terminal import (
    safe_print,
    status_print,
    success_print,
    error_print,
)

from resolver import decide_application
from brain.execution_result import ExecutionResult

from response_utils import classify_response

NAME = "Open Application"
INTENT = "open_app"
DESCRIPTION = "Launches desktop applications."
VERSION = "1.6"
AUTHOR = "Harshith"


# ============================================================
# CHROME DISCOVERY
# ============================================================

def find_chrome_executable():
    """
    Dynamically locate Google Chrome through the Windows registry.

    No user-specific paths are hardcoded.
    """

    registry_locations = [
        (
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
        ),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
        ),
    ]

    for hive, key_path in registry_locations:

        try:

            with winreg.OpenKey(
                hive,
                key_path
            ) as key:

                executable = winreg.QueryValue(
                    key,
                    None
                )

                if executable and os.path.isfile(executable):
                    return executable

        except (
            FileNotFoundError,
            OSError
        ):
            continue

    return None


def is_chrome_running():
    """
    Check whether Chrome is currently running.

    Uses Windows task information rather than a hardcoded
    process/window path.
    """

    try:

        result = subprocess.run(
            [
                "tasklist",
                "/FI",
                "IMAGENAME eq chrome.exe"
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        return "chrome.exe" in result.stdout.lower()

    except Exception:
        return False


def focus_chrome_window():
    """
    Bring an existing visible Chrome window to the foreground.

    Returns True if a Chrome window was successfully found.
    """

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    EnumWindowsProc = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HWND,
        wintypes.LPARAM
    )

    found_window = None

    def enum_window_callback(hwnd, _):

        nonlocal found_window

        if found_window:
            return False

        # Ignore invisible windows.
        if not user32.IsWindowVisible(hwnd):
            return True

        # Get owning process ID.
        process_id = wintypes.DWORD()

        user32.GetWindowThreadProcessId(
            hwnd,
            ctypes.byref(process_id)
        )

        if not process_id.value:
            return True

        # Open the process so we can inspect its executable name.
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

        process_handle = kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION,
            False,
            process_id.value
        )

        if not process_handle:
            return True

        try:

            buffer_size = wintypes.DWORD(260)

            buffer = ctypes.create_unicode_buffer(
                buffer_size.value
            )

            success = kernel32.QueryFullProcessImageNameW(
                process_handle,
                0,
                buffer,
                ctypes.byref(buffer_size)
            )

            if not success:
                return True

            executable_name = os.path.basename(
                buffer.value
            ).lower()

            if executable_name != "chrome.exe":
                return True

            found_window = hwnd

            return False

        finally:

            kernel32.CloseHandle(
                process_handle
            )

    callback = EnumWindowsProc(
        enum_window_callback
    )

    user32.EnumWindows(
        callback,
        0
    )

    if not found_window:
        return False

    # Restore the window if minimized.
    SW_RESTORE = 9

    user32.ShowWindow(
        found_window,
        SW_RESTORE
    )

    # Bring Chrome to the foreground.
    user32.SetForegroundWindow(
        found_window
    )

    return True


def launch_chrome():
    """
    Open Google Chrome intelligently.

    If Chrome is already running:
        Bring an existing Chrome window to the foreground.

    If Chrome is not running:
        Launch Chrome using its dynamically discovered executable.

    No Chrome profile is selected or hardcoded.
    """

    # --------------------------------------------------------
    # Chrome already running
    # --------------------------------------------------------

    if is_chrome_running():

        if focus_chrome_window():
            return True

    # --------------------------------------------------------
    # Chrome is not running
    # --------------------------------------------------------

    executable = find_chrome_executable()

    if not executable:
        return False

    subprocess.Popen(
        [
            executable
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL
    )

    return True


# ============================================================
# APPLICATION LAUNCHER
# ============================================================

def launch_application(match):

    app_name = match["name"]
    launch_target = match["launch_target"]
    source = match["source"]

    try:

        # ========================================================
        # GOOGLE CHROME
        # ========================================================

        if app_name.lower().strip() == "google chrome":

            if not launch_chrome():

                raise RuntimeError(
                    "Google Chrome could not be launched."
                )


        # ========================================================
        # START MENU APPLICATION
        # ========================================================

        elif source == "start_menu":

            os.startfile(
                launch_target
            )


        # ========================================================
        # WINDOWS PACKAGED APPLICATION
        # ========================================================

        elif source == "windows_app":

            import ctypes

            result = ctypes.windll.shell32.ShellExecuteW(
                None,
                "open",
                f"shell:AppsFolder\\{launch_target}",
                None,
                None,
                1
            )

            # ShellExecuteW returns a value <= 32 on failure.
            if result <= 32:

                raise RuntimeError(
                    f"Windows could not launch the application "
                    f"(error code {result})."
                )


        # ========================================================
        # UNKNOWN SOURCE
        # ========================================================

        else:

            raise RuntimeError(
                f"Unknown application source: '{source}'."
            )


        # ========================================================
        # REPORT SUCCESS
        # ========================================================

        status_print(
            f"🚀 Opening {app_name}..."
        )

        success_print(
            f"{app_name.title()} opened."
        )

        return ExecutionResult(
            handled=True,
            success=True
        )


    except Exception as error:

        error_print(
            f"❌ Couldn't open '{app_name}'.\n"
            f"Reason: {error}"
        )

        return ExecutionResult(
            handled=True,
            success=False
        )


# ============================================================
# PENDING RESPONSE HANDLER
# ============================================================

def handle_pending_response(
    pending,
    user_input
):

    response = classify_response(
        user_input
    )
    cancel_words = {
        "cancel",
        "stop",
        "nevermind",
        "never mind"
    }

    yes_words = {
        "yes",
        "y",
        "yeah",
        "yep",
        "yup",
        "sure",
        "okay",
        "ok",
        "correct",
        "do it"
    }

    no_words = {
        "no",
        "n",
        "nope",
        "nah"
    }

    # ---------------------------------
    # Cancel
    # ---------------------------------

    if response in cancel_words:

        safe_print(
            "👍 Okay, operation cancelled."
        )

        return None

    status = pending["status"]

    # ---------------------------------
    # Normal application confirmation
    # ---------------------------------

    if status == "confirmation_required":

        if response in yes_words:

            launch_application(
                pending["match"]
            )

            return None

        if response in no_words:

            safe_print(
                "👍 Okay, cancelled."
            )

            return None

        safe_print(
            "🤖 Please answer yes or no."
        )

        return pending

    # ---------------------------------
    # Web fallback confirmation
    # ---------------------------------

    if status == "web_fallback_confirmation_required":

        if response in yes_words:

            from skills.open_web import execute as open_web

            task = pending["task"]

            return open_web(
                task
            )

        if response in no_words:

            safe_print(
                "👍 Okay, operation cancelled."
            )

            return None

        safe_print(
            "🤖 Please answer yes or no."
        )

        return pending

    # ---------------------------------
    # Application selection
    # ---------------------------------

    if status == "selection_required":

        candidates = pending["candidates"]

        cancel_number = len(candidates) + 1

        if response.isdigit():

            choice = int(response)

            if 1 <= choice <= len(candidates):

                launch_application(
                    candidates[choice - 1]
                )

                return None

            if choice == cancel_number:

                safe_print(
                    "👍 Operation cancelled."
                )

                return None

        safe_print(
            f"🤖 Choose a number from 1 to "
            f"{cancel_number}, or type 'cancel'."
        )

        return pending

    return None


# ============================================================
# SKILL EXECUTION
# ============================================================

def execute(task):

    data = task.data or {}

    query = (
        data.get("target")
        or task.target
        or ""
    ).strip()

    if not query:

        return ExecutionResult(
            handled=True,
            success=False,
            message="❌ No application specified."
        )

    # ---------------------------------
    # Resolve installed application
    # ---------------------------------

    decision = decide_application(
        query
    )

    status = decision["status"]

    # ---------------------------------
    # Application found confidently
    # ---------------------------------

    if status == "resolved":

        return launch_application(
            decision["match"]
        )

    # ---------------------------------
    # Application found, confirmation
    # is required
    # ---------------------------------

    if status == "confirm":

        match = decision["match"]

        safe_print(
            f"🤖 Did you mean "
            f"{match['name']}? (yes/no)"
        )

        return {
            "status": "confirmation_required",
            "match": match
        }

    # ---------------------------------
    # Multiple possible applications
    # ---------------------------------

    if status == "ambiguous":

        candidates = [
            decision["match"],
            *decision["alternatives"]
        ]

        lines = []

        lines.append(
            "🤔 I found multiple possible applications:"
        )

        lines.append("")

        for index, candidate in enumerate(
            candidates,
            start=1
        ):

            lines.append(
                f"{index}. {candidate['name']}"
            )

        lines.append("")

        lines.append(
            f"{len(candidates) + 1}. Cancel operation"
        )

        safe_print(
            "\n".join(lines)
        )

        return {
            "status": "selection_required",
            "candidates": candidates
        }

    # ---------------------------------
    # Application NOT found
    # ---------------------------------

    if status == "not_found":

        safe_print(
            f"🔎 I couldn't find an installed "
            f"application named '{query}'."
        )

        safe_print(
            f"🌐 Do you want me to open "
            f"'{query}' on the web instead? (yes/no)"
        )

        return {
            "status": "web_fallback_confirmation_required",
            "task": task
        }

    # ---------------------------------
    # Unexpected resolver status
    # ---------------------------------

    return ExecutionResult(
        handled=True,
        success=False,
        message=(
            f"❌ Couldn't determine how to open "
            f"'{query}'."
        )
    )