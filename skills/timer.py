import re
import threading

from terminal import safe_print


NAME = "Timer"
INTENT = "timer"
DESCRIPTION = "Starts, lists, and cancels timers."
VERSION = "1.2"
AUTHOR = "Harshith"


ACTIVE_TIMERS = {}
TIMER_COUNTER = 0
TIMER_LOCK = threading.Lock()
TIMER_LABEL_WORDS = {"called", "named", "as", "titled", "labelled", "labelled as"}

def extract_timer_name(text):

    patterns = [
        # set a timer called study for 5 seconds
        r"\b(?:called|named)\s+(.+?)\s+(?:for|after|in)\s+\d+\s*-?\s*(?:seconds?|minutes?|hours?)\b",

        # set a timer for 5 seconds called study
        r"\d+\s*-?\s*(?:seconds?|minutes?|hours?)\s+(?:called|named)\s+(.+)$"
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:
            timer_name = match.group(1).strip()

            if timer_name:
                return timer_name

    return None

def parse_duration(text):
    patterns = {
        "hour": 3600,
        "minute": 60,
        "second": 1
    }

    for unit, multiplier in patterns.items():
        match = re.search(
            rf"(\d+)\s*-?\s*{unit}s?",
            text
        )

        if match:
            value = int(match.group(1))
            return value * multiplier, f"{value} {unit}{'' if value == 1 else 's'}"

    return None, None


def finish_timer(timer_id, duration_label):
    with TIMER_LOCK:
        timer_data = ACTIVE_TIMERS.pop(timer_id, None)

    if timer_data is None:
        return

    timer_name = timer_data.get("name")

    if timer_name:
        safe_print(f"\n⏰ Your '{timer_name}' timer is finished!")
    else:
        safe_print(f"\n⏰ Timer #{timer_id} finished after {duration_label}.")

def start_timer(seconds, duration_label, timer_name=None):
    global TIMER_COUNTER

    with TIMER_LOCK:
        TIMER_COUNTER += 1
        timer_id = TIMER_COUNTER

        timer = threading.Timer(
            seconds,
            finish_timer,
            args=(timer_id, duration_label)
        )

        ACTIVE_TIMERS[timer_id] = {
            "timer": timer,
            "duration_label": duration_label,
            "name": timer_name,
            "seconds": seconds
        }

        timer.start()

    if timer_name:
        safe_print(
            f"⏱️ Timer #{timer_id} '{timer_name}' started for "
            f"{duration_label}."
        )
    else:
        safe_print(
            f"⏱️ Timer #{timer_id} started for {duration_label}."
        )


def list_timers():
    with TIMER_LOCK:
        timers = list(ACTIVE_TIMERS.items())

    if not timers:
        safe_print("⏱️ No active timers.")
        return

    lines = []

    lines.append("⏱️ Active timers:")
    lines.append("")

    for timer_id, timer_data in timers:
        timer_name = timer_data["name"]
        duration_label = timer_data["duration_label"]

        if timer_name:
            lines.append(
                f"{timer_id}. {timer_name} — {duration_label}"
            )
        else:
            lines.append(
                f"{timer_id}. {duration_label}"
            )

    safe_print("\n".join(lines))


def cancel_timer(timer_id):
    with TIMER_LOCK:
        timer_data = ACTIVE_TIMERS.pop(timer_id, None)

    if timer_data is None:
        safe_print(f"❌ Timer #{timer_id} doesn't exist.")
        return

    timer_data["timer"].cancel()

    timer_name = timer_data.get("name")

    if timer_name:
        safe_print(f"👍 Cancelled the '{timer_name}' timer.")
    else:
        safe_print(f"👍 Timer #{timer_id} cancelled.")
    
def cancel_timer_by_name(timer_name):
    timer_name = timer_name.lower().strip()

    with TIMER_LOCK:
        matches = [
            (timer_id, timer_data)
            for timer_id, timer_data in ACTIVE_TIMERS.items()
            if timer_data.get("name")
            and timer_data["name"].lower() == timer_name
        ]

    if not matches:
        safe_print(f"❌ I couldn't find an active timer named '{timer_name}'.")
        return

    if len(matches) > 1:
        lines = []

        lines.append(f"🤔 I found multiple timers named '{timer_name}':")
        lines.append("")

        for timer_id, timer_data in matches:
            lines.append(
                f"{timer_id}. {timer_data['name']} — "
                f"{timer_data['duration_label']}"
            )

        lines.append("")
        lines.append("💡 Cancel one using its timer number.")

        safe_print("\n".join(lines))
        return

    timer_id, _ = matches[0]
    cancel_timer(timer_id)

def cancel_all_timers():
    with TIMER_LOCK:
        timers = list(ACTIVE_TIMERS.values())
        ACTIVE_TIMERS.clear()

    if not timers:
        safe_print("⏱️ No active timers to cancel.")
        return

    for timer_data in timers:
        timer_data["timer"].cancel()

    safe_print("👍 All active timers cancelled.")


def execute(task):
    raw_text = task.data.get("raw_command", "").lower().strip()
    routing_text = task.data.get("routing_text", raw_text).lower().strip()

    # LIST TIMERS
    if (
        "list timer" in routing_text
        or "show timer" in routing_text
        or "active timer" in routing_text
    ):
        list_timers()
        return

    # CANCEL ALL TIMERS
    if (
        "cancel all timer" in routing_text
        or "stop all timer" in routing_text
    ):
        cancel_all_timers()
        return

    # CANCEL ONE TIMER
    cancel_match = re.search(
        r"(?:cancel|stop)\s+timer\s+#?(\d+)",
        routing_text
    )

    if cancel_match:
        timer_id = int(cancel_match.group(1))
        cancel_timer(timer_id)
        return

    # CANCEL TIMER BY NAME
    cancel_name_match = re.search(
        r"(?:cancel|stop)\s+(?:my\s+)?timer\s+(.+)$",
        routing_text
    )

    if cancel_name_match:
        timer_name = cancel_name_match.group(1).strip()
        cancel_timer_by_name(timer_name)
        return


    cancel_natural_match = re.search(
        r"(?:cancel|stop)\s+(?:my\s+)?(.+?)\s+timer$",
        routing_text
    )

    if cancel_natural_match:
        timer_name = cancel_natural_match.group(1).strip()
        cancel_timer_by_name(timer_name)
        return

    # START TIMER
    seconds, duration_label = parse_duration(raw_text)

    if seconds is None:
        safe_print("❌ I couldn't understand the timer duration.")
        return

    timer_name = extract_timer_name(raw_text)

    start_timer(
        seconds,
        duration_label,
        timer_name
    )