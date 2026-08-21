import time
import threading

import win32gui
import win32process
import psutil

from brain import bus
from brain.application_identity import (
    application_identity
)


class Observer:

    def __init__(self):

        self.running = False

        self.last_hwnd = None
        self.last_pid = None


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


    def get_window_info(
        self,
        hwnd
    ):

        title = win32gui.GetWindowText(
            hwnd
        )

        pid = None
        process_name = None
        executable = None
        application = "Unknown"


        try:

            _, pid = (
                win32process.GetWindowThreadProcessId(
                    hwnd
                )
            )

            process = psutil.Process(
                pid
            )

            process_name = process.name()

            executable = process.exe()

            application = application_identity.resolve(
                executable=executable,
                process=process_name
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):

            pass


        return {
            "hwnd": hwnd,
            "title": title,
            "application": application,
            "pid": pid,
            "process": process_name,
            "executable": executable,
            "timestamp": time.time()
        }


    def loop(self):

        ignored = {
            "",
            "Task Switching",
            "Program Manager",
            "Windows Input Experience",
        }


        while self.running:

            hwnd = (
                win32gui.GetForegroundWindow()
            )


            if not hwnd:

                time.sleep(0.5)

                continue


            info = self.get_window_info(
                hwnd
            )

            title = info["title"]

            pid = info["pid"]


            if title in ignored:

                time.sleep(0.5)

                continue


            # ---------------------------------
            # Detect actual window/application
            # change.
            #
            # Title changes inside the same
            # window do NOT create a new
            # foreground event.
            # ---------------------------------

            window_changed = (
                hwnd != self.last_hwnd
                or pid != self.last_pid
            )


            if window_changed:

                self.last_hwnd = hwnd

                self.last_pid = pid

                bus.emit(
                    "window_changed",
                    info
                )


            time.sleep(0.5)


observer = Observer()