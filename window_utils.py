import ctypes
from ctypes import wintypes
import subprocess

user32 = ctypes.windll.user32

def get_process_name(pid):

    try:
        result = subprocess.run(
            [
                "tasklist",
                "/FI",
                f"PID eq {pid}",
                "/FO",
                "CSV",
                "/NH"
            ],
            capture_output=True,
            text=True
        )

        line = result.stdout.strip()

        if not line:
            return None

        return line.split(",")[0].strip('"')

    except Exception:
        return None

def get_open_windows():

    windows = []

    EnumWindows = user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        wintypes.HWND,
        wintypes.LPARAM
    )

    GetWindowText = user32.GetWindowTextW
    GetWindowTextLength = user32.GetWindowTextLengthW

    IsWindowVisible = user32.IsWindowVisible

    GetWindowThreadProcessId = user32.GetWindowThreadProcessId

    callback = None

    def foreach_window(hwnd, lParam):

        if not IsWindowVisible(hwnd):
            return True

        length = GetWindowTextLength(hwnd)

        if length == 0:
            return True

        buffer = ctypes.create_unicode_buffer(length + 1)

        GetWindowText(hwnd, buffer, length + 1)

        title = buffer.value.strip()

        if not title:
            return True

        pid = wintypes.DWORD()

        GetWindowThreadProcessId(
            hwnd,
            ctypes.byref(pid)
        )
        process=get_process_name(pid.value)
        windows.append(
            {
                "title": title,
                "pid": pid.value,
                "process": process,
                "hwnd": hwnd
            }
        )

        return True

    callback = EnumWindowsProc(foreach_window)

    EnumWindows(callback, 0)

    return windows

if __name__ == "__main__":

    for window in get_open_windows():
        print(window)