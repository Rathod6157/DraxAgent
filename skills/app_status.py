import subprocess

from terminal import safe_print
from skills.close_app import PROCESS_ALIASES


NAME = "Application Status"
INTENT = "app_status"
DESCRIPTION = "Checks whether applications are running."
VERSION = "1.0"
AUTHOR = "Harshith"


def get_running_processes():

    result = subprocess.run(
        ["tasklist", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        check=True
    )

    processes = []

    for line in result.stdout.splitlines():

        process_name = line.split(",")[0].strip('"')

        if process_name not in processes:
            processes.append(process_name)

    return processes


def is_application_running(app_name):

    running_processes = get_running_processes()

    aliases = PROCESS_ALIASES.get(app_name.lower())

    if aliases:

        return any(
            process.lower() == alias.lower()
            for process in running_processes
            for alias in aliases
        )

    search_words = app_name.lower().split()

    return any(
        any(word in process.lower() for word in search_words)
        for process in running_processes
    )

def list_running_applications():

    running_processes = get_running_processes()

    ignored_processes = {
        "system",
        "registry",
        "smss.exe",
        "csrss.exe",
        "wininit.exe",
        "services.exe",
        "lsass.exe",
        "svchost.exe",
        "fontdrvhost.exe",
        "dwm.exe",
        "explorer.exe"
    }

    visible_processes = [
        process
        for process in running_processes
        if process.lower() not in ignored_processes
    ]

    if not visible_processes:
        safe_print("❌ I couldn't find any running applications.")
        return

    safe_print("🖥️ Running applications:")

    for process in visible_processes:
        safe_print(f"   • {process}")
def execute(task):

    query = task.data.get("target", "").strip()
    if query == "__list_running_apps__":
        list_running_applications()
        return

    if not query:
        safe_print("❌ No application specified.")
        return

    if is_application_running(query):
        safe_print(f"✅ Yes, {query} is running.")
    else:
        safe_print(f"❌ No, {query} is not running.")