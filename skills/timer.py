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


def finish_timer(timer_id, label):
    with TIMER_LOCK:
        timer_data = ACTIVE_TIMERS.pop(timer_id, None)

    # Timer may already have been cancelled.
    if timer_data is None:
        return

    safe_print(f"\n⏰ Timer #{timer_id} finished: {label}")


def start_timer(seconds, label):
    global TIMER_COUNTER

    with TIMER_LOCK:
        TIMER_COUNTER += 1
        timer_id = TIMER_COUNTER

        timer = threading.Timer(
            seconds,
            finish_timer,
            args=(timer_id, label)
        )

        ACTIVE_TIMERS[timer_id] = {
            "timer": timer,
            "label": label,
            "seconds": seconds
        }

        timer.start()

    safe_print(f"⏱️ Timer #{timer_id} started for {label}.")


def list_timers():
    with TIMER_LOCK:
        timers = list(ACTIVE_TIMERS.items())

    if not timers:
        safe_print("⏱️ No active timers.")
        return

    safe_print("⏱️ Active timers:")

    for timer_id, timer_data in timers:
        safe_print(
            f"{timer_id}. {timer_data['label']}"
        )


def cancel_timer(timer_id):
    with TIMER_LOCK:
        timer_data = ACTIVE_TIMERS.pop(timer_id, None)

    if timer_data is None:
        safe_print(f"❌ Timer #{timer_id} doesn't exist.")
        return

    timer_data["timer"].cancel()

    safe_print(f"👍 Timer #{timer_id} cancelled.")


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
    text = task.data.get("target", "").lower().strip()

    # LIST TIMERS
    if (
        "list timers" in text
        or "show timers" in text
        or "active timers" in text
    ):
        list_timers()
        return

    # CANCEL ALL TIMERS
    if (
        "cancel all timers" in text
        or "stop all timers" in text
    ):
        cancel_all_timers()
        return

    # CANCEL ONE TIMER
    cancel_match = re.search(
        r"(?:cancel|stop)\s+timer\s+#?(\d+)",
        text
    )

    if cancel_match:
        timer_id = int(cancel_match.group(1))
        cancel_timer(timer_id)
        return

    # START TIMER
    seconds, label = parse_duration(text)

    if seconds is None:
        safe_print("❌ I couldn't understand the timer duration.")
        return

    start_timer(seconds, label)