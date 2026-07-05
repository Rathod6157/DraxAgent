from prompt_toolkit import print_formatted_text
from prompt_toolkit.patch_stdout import patch_stdout


def safe_print(*args, **kwargs):
    message = " ".join(str(arg) for arg in args)
    print_formatted_text(message)


def terminal_session():
    return patch_stdout(raw=True)