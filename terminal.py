import os

from prompt_toolkit import print_formatted_text
from prompt_toolkit.patch_stdout import patch_stdout


_gui_callback = None


def set_output_callback(callback):
    global _gui_callback
    _gui_callback = callback


def clear_output_callback():
    global _gui_callback
    _gui_callback = None


def emit(
    text,
    message_type="assistant"
):

    if _gui_callback:
        _gui_callback(
            text,
            message_type
        )

    # ---------------------------------------------------------
    # Tauri / GUI mode
    # ---------------------------------------------------------
    #
    # The Tauri Python bridge does NOT have a Windows console.
    # prompt_toolkit expects one and crashes with:
    #
    # NoConsoleScreenBufferError
    #
    # So in bridge mode we send structured data through the
    # bridge instead of trying to print to a terminal.
    # ---------------------------------------------------------

    if os.environ.get(
        "DRAX_BRIDGE"
    ) == "1":

        return

    print_formatted_text(
        text
    )


def safe_print(
    *args,
    **kwargs
):

    emit(
        " ".join(
            str(arg)
            for arg in args
        ),
        "assistant"
    )


def status_print(
    *args
):

    emit(
        " ".join(
            str(arg)
            for arg in args
        ),
        "status"
    )


def status_done_print(
    *args
):

    emit(
        " ".join(
            str(arg)
            for arg in args
        ),
        "status_done"
    )


def success_print(
    *args
):

    emit(
        " ".join(
            str(arg)
            for arg in args
        ),
        "success"
    )


def error_print(
    *args
):

    emit(
        " ".join(
            str(arg)
            for arg in args
        ),
        "error"
    )


def terminal_session():

    return patch_stdout(
        raw=True
    )