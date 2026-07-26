import time
import threading

import win32gui

from brain import bus


class Observer:

    def __init__(self):

        self.running = False
        self.last_window = None

    def start(self):

        if self.running:
            return

        self.running = True

        threading.Thread(
            target=self.loop,
            daemon=True
        ).start()

    def stop(self):

        self.running = False

    def loop(self):

        while self.running:

            hwnd = win32gui.GetForegroundWindow()

            title = win32gui.GetWindowText(hwnd)
            
            ignored = {
                "",
                "Task Switching",
                "Program Manager",
                "Windows Input Experience",
            }

            if title in ignored:
                time.sleep(0.5)
                continue

            if title and title != self.last_window:

                self.last_window = title

                bus.emit(
                    "window_changed",
                    {
                        "title": title,
                        "timestamp": time.time()
                    }
                )

            time.sleep(0.5)


observer = Observer()