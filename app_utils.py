import os
import subprocess
import json
from difflib import get_close_matches


def get_start_menu_apps():

    apps = {}

    folders = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expandvars(
            r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"
        )
    ]

    for folder in folders:

        if not os.path.exists(folder):
            continue

        for root, _, files in os.walk(folder):

            for file in files:

                if file.endswith(".lnk"):

                    name = os.path.splitext(file)[0].lower()

                    apps[name] = os.path.join(root, file)

    return apps

def get_windows_apps():

    powershell_command = """
    Get-StartApps |
    Select-Object Name, AppID |
    ConvertTo-Json -Compress
    """

    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                powershell_command
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode != 0:
            return {}

        data = json.loads(result.stdout)

        if isinstance(data, dict):
            data = [data]

        apps = {}

        for app in data:

            name = app.get("Name")
            app_id = app.get("AppID")

            if name and app_id:
                apps[name.lower()] = app_id

        return apps

    except (json.JSONDecodeError, OSError):
        return {}

def get_all_applications():

    apps = {}

    for name, path in get_start_menu_apps().items():
        apps[name] = {
            "name": name,
            "launch_target": path,
            "source": "start_menu"
        }

    for name, app_id in get_windows_apps().items():

        apps[name] = {
            "name": name,
            "launch_target": app_id,
            "source": "windows_app"
        }

    return apps

def find_application(app_name):
    """
    Returns the best executable or shortcut path
    for the requested application.

    Returns None if nothing is found.
    """
    apps = get_start_menu_apps()
    
    if not app_name.strip():
        return None
    
    # Exact match
    if app_name.lower() in apps:
        return apps[app_name.lower()]

    # Score match
    best_score = 0
    best_path = None

    query_words = app_name.lower().split()

    for name, path in apps.items():

        score = 0
        app_words = name.split()

        for word in query_words:
            if word in app_words:
                score += 10
        score -= abs(len(app_words) - len(query_words))

        if score > best_score:
            best_score = score
            best_path = path

    if best_score > 0:
        return best_path
    # Fuzzy match
    matches = get_close_matches(
        app_name.lower(),
        apps.keys(),
        n=1,
        cutoff=0.5
    )

    if matches:
        return apps[matches[0]]

    return None

if __name__ == "__main__":

    print(find_application("chrome"))
    print(find_application("microsoft edge"))
    print(find_application("obs"))