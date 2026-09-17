import ctypes
import threading
import time
from ctypes import wintypes

from terminal import safe_print


user32 = ctypes.windll.user32

EnumWindowsProc = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HWND,
    wintypes.LPARAM,
)


def _window_title(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value.strip()


def _window_pid(hwnd):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return int(pid.value)


def _visible_windows():
    windows = []

    @EnumWindowsProc
    def callback(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True

        title = _window_title(hwnd)
        if not title:
            return True

        windows.append({
            "hwnd": int(hwnd),
            "title": title,
            "pid": _window_pid(hwnd),
        })
        return True

    user32.EnumWindows(callback, 0)
    return windows


def find_windows(target):
    target = str(target or "").strip().lower()
    if not target:
        return []

    results = []
    for window in _visible_windows():
        title = window["title"].lower()
        if target in title:
            results.append(window)

    # Also allow a process name match.
    try:
        import psutil
        for process in psutil.process_iter(["pid", "name"]):
            name = str(process.info.get("name") or "").lower()
            if target in name:
                for window in _visible_windows():
                    if window["pid"] == process.info["pid"] and window not in results:
                        results.append(window)
    except Exception:
        pass

    return results


def is_window_responsive(hwnd):
    try:
        # IsHungAppWindow is specifically intended to identify
        # windows that have stopped responding to Windows messages.
        return not bool(user32.IsHungAppWindow(wintypes.HWND(hwnd)))
    except Exception:
        return True


def status(target):
    windows = find_windows(target)

    if not windows:
        return {
            "success": False,
            "found": False,
            "target": target,
            "message": f"I couldn't find an open window for '{target}'.",
        }

    states = []
    for window in windows:
        responsive = is_window_responsive(window["hwnd"])
        states.append({
            **window,
            "responsive": responsive,
            "status": "responding" if responsive else "not_responding",
        })

    return {
        "success": True,
        "found": True,
        "target": target,
        "windows": states,
        "responsive": all(item["responsive"] for item in states),
        "message": (
            f"'{target}' is responding."
            if all(item["responsive"] for item in states)
            else f"'{target}' is not responding."
        ),
    }


def watch_until_responsive(target, timeout=300, interval=2.0, callback=None):
    target = str(target or "").strip()

    def worker():
        deadline = time.monotonic() + float(timeout)
        saw_hung = False

        while time.monotonic() < deadline:
            result = status(target)

            if result.get("found"):
                if not result.get("responsive"):
                    saw_hung = True
                elif saw_hung:
                    message = f"🟢 {target} is responding again."
                    if callback:
                        callback(message, result)
                    else:
                        safe_print(message)
                    return

            time.sleep(max(0.5, float(interval)))

        if callback:
            callback(
                f"⏱️ I stopped watching '{target}' after {int(timeout)} seconds.",
                {"success": False, "timeout": True, "target": target},
            )
        else:
            safe_print(
                f"⏱️ I stopped watching '{target}' after {int(timeout)} seconds."
            )

    thread = threading.Thread(
        target=worker,
        name=f"DraxWatch-{target}",
        daemon=True,
    )
    thread.start()

    return {
        "success": True,
        "started": True,
        "target": target,
        "timeout": timeout,
        "interval": interval,
    }
