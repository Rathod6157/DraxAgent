from prompt_toolkit import print_formatted_text
from prompt_toolkit.patch_stdout import patch_stdout


_gui_callback = None


def set_output_callback(callback):
    global _gui_callback
    _gui_callback = callback


def clear_output_callback():
    global _gui_callback
    _gui_callback = None


def safe_print(*args, **kwargs):
    message = " ".join(str(arg) for arg in args)

    if _gui_callback:
        _gui_callback(message)

    print_formatted_text(message)


def terminal_session():
    return patch_stdout(raw=True)