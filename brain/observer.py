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

    # ---------------------------------
    # Windows that belong to Drax itself
    # ---------------------------------

    IGNORED_TITLES = {
        "",
        "Task Switching",
        "Program Manager",
        "Windows Input Experience",

        # Drax main window
        "DraxAgent",

        # Drax summon window
        "Drax",
    }


    def __init__(self):

        self.running = False

        self.last_hwnd = None
        self.last_pid = None
        self.last_title = None


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


    def is_ignored_window(
        self,
        info
    ):

        title = info.get(
            "title",
            ""
        )

        return title in self.IGNORED_TITLES


    def loop(self):

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


            # ---------------------------------
            # Ignore Drax / system windows.
            #
            # IMPORTANT:
            # We do NOT update last_hwnd or
            # last_pid here.
            #
            # This means Drax temporarily
            # appearing on screen does not
            # destroy the previous real
            # activity.
            # ---------------------------------

            if self.is_ignored_window(info):

                time.sleep(0.5)

                continue


            title = info["title"]

            pid = info["pid"]


            # ---------------------------------
            # Detect actual external window
            # change.
            # ---------------------------------

            window_changed = (
                hwnd != self.last_hwnd
                or pid != self.last_pid
                or title != self.last_title
            )


            if window_changed:

                self.last_hwnd = hwnd

                self.last_pid = pid
                
                self.last_title = title

                bus.emit(
                    "window_changed",
                    info
                )


            time.sleep(0.5)


observer = Observer()