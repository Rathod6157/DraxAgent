from window_utils import get_open_windows

from terminal import safe_print
from skills.close_app import PROCESS_ALIASES


NAME = "Application Status"
INTENT = "app_status"
DESCRIPTION = "Checks applications, running status, and open windows."
VERSION = "1.0"
AUTHOR = "Harshith"





def is_application_running(app_name):

    windows = get_open_windows()

    search_words = app_name.lower().split()

    for window in windows:

        title = window["title"].lower()

        if all(word in title for word in search_words):
            return True

    return False

def list_running_applications():

    windows = get_open_windows()

    ignored_titles = {
        "Program Manager",
        "Windows Input Experience"
    }

    seen = set()
    visible = []

    for window in windows:

        title = window["title"]

        if title in ignored_titles:
            continue

        if title in seen:
            continue

        seen.add(title)
        visible.append(title)

    if not visible:
        safe_print("❌ I couldn't find any open windows.")
        return

    lines = []

    lines.append("🖥️ Open windows:")
    lines.append("")

    for title in visible:
        lines.append(f"• {title}")

    safe_print("\n".join(lines))
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