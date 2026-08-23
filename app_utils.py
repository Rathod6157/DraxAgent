import os
import subprocess
import json
from difflib import get_close_matches

from terminal import safe_print


# ============================================================
# Start Menu Applications
# ============================================================

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

                if not file.lower().endswith(".lnk"):
                    continue

                name = os.path.splitext(file)[0].strip().lower()

                if not name:
                    continue

                apps[name] = os.path.join(
                    root,
                    file
                )

    return apps


# ============================================================
# Windows / Microsoft Store Applications
# ============================================================

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
            errors="replace",
            timeout=15
        )

        if result.returncode != 0:
            return {}

        if not result.stdout.strip():
            return {}

        data = json.loads(
            result.stdout
        )

        if isinstance(data, dict):
            data = [data]

        apps = {}

        for app in data:

            name = app.get("Name")
            app_id = app.get("AppID")

            if name and app_id:

                apps[name.strip().lower()] = app_id

        return apps

    except (
        json.JSONDecodeError,
        OSError,
        subprocess.TimeoutExpired
    ):

        return {}


# ============================================================
# Resolve Shortcut Target
# ============================================================
#
# Kept for compatibility with the rest of Drax.
#
# IMPORTANT:
# We DO NOT call this for every shortcut during application
# indexing anymore.
#
# Start Menu .lnk files can be launched directly with
# os.startfile(), so resolving every target beforehand is
# unnecessary and extremely slow.
#
# ============================================================

def resolve_shortcut_target(
    shortcut
):

    powershell_command = f"""
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut('{shortcut}')
    $shortcut.TargetPath
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
            errors="replace",
            timeout=5
        )

        if result.returncode != 0:
            return None

        target = result.stdout.strip()

        if not target:
            return None

        return target

    except (
        OSError,
        subprocess.TimeoutExpired
    ):

        return None


# ============================================================
# Combined Application Index
# ============================================================

def get_all_applications():

    apps = {}

    # ---------------------------------
    # Start Menu applications
    # ---------------------------------

    start_menu_apps = get_start_menu_apps()

    for name, path in start_menu_apps.items():

        apps[name] = {

            "name": name,

            # The .lnk itself is the launch target.
            # Windows resolves it when launched.
            "launch_target": path,

            "source": "start_menu",

            # We no longer resolve every shortcut here.
            # This keeps indexing fast.
            "executable": None
        }


    # ---------------------------------
    # Windows applications
    # ---------------------------------

    windows_apps = get_windows_apps()

    for name, app_id in windows_apps.items():

        apps[name] = {

            "name": name,

            "launch_target": app_id,

            "source": "windows_app",

            "executable": None
        }


    return apps


# ============================================================
# Legacy Application Finder
# ============================================================

def find_application(
    app_name
):

    """
    Returns the best executable or
    shortcut path for the requested
    application.
    """

    apps = get_start_menu_apps()

    if not app_name.strip():

        return None


    # ---------------------------------
    # Exact match
    # ---------------------------------

    query = app_name.lower().strip()

    if query in apps:

        return apps[query]


    # ---------------------------------
    # Score match
    # ---------------------------------

    best_score = 0
    best_path = None

    query_words = query.split()

    for name, path in apps.items():

        score = 0

        app_words = name.split()

        for word in query_words:

            if word in app_words:

                score += 10

        score -= abs(
            len(app_words)
            - len(query_words)
        )

        if score > best_score:

            best_score = score

            best_path = path


    if best_score > 0:

        return best_path


    # ---------------------------------
    # Fuzzy match
    # ---------------------------------

    matches = get_close_matches(
        query,
        apps.keys(),
        n=1,
        cutoff=0.5
    )

    if matches:

        return apps[
            matches[0]
        ]

    return None


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    safe_print(
        find_application(
            "chrome"
        )
    )

    safe_print(
        find_application(
            "microsoft edge"
        )
    )

    safe_print(
        find_application(
            "obs"
        )
    )