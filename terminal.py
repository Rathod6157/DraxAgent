from prompt_toolkit import print_formatted_text
from prompt_toolkit.patch_stdout import patch_stdout

_gui_callback = None


def set_output_callback(callback):
    global _gui_callback
    _gui_callback = callback


def clear_output_callback():
    global _gui_callback
    _gui_callback = None


def emit(text, message_type="assistant"):

    if _gui_callback:
        _gui_callback(text, message_type)

    print_formatted_text(text)


def safe_print(*args, **kwargs):
    emit(
        " ".join(str(arg) for arg in args),
        "assistant"
    )


def status_print(*args):
    emit(
        " ".join(str(arg) for arg in args),
        "status"
    )


def success_print(*args):
    emit(
        " ".join(str(arg) for arg in args),
        "success"
    )


def error_print(*args):
    emit(
        " ".join(str(arg) for arg in args),
        "error"
    )


def terminal_session():
    return patch_stdout(raw=True)