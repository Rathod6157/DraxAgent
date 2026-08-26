import webbrowser
from urllib.parse import quote_plus

from terminal import (
    status_print,
    success_print,
    error_print,
)

from brain.execution_result import (
    ExecutionResult
)

from web_resolver import (
    resolve_web_destination
)

NAME = "Open Web"
INTENT = "open_web"
DESCRIPTION = "Opens websites and web destinations."
VERSION = "1.1"
AUTHOR = "Harshith"


def build_url(destination):
    """
    Convert a natural web destination into a URL.

    Examples:

        YouTube
            -> Google 'I'm Feeling Lucky' URL

        Spotify
            -> Google 'I'm Feeling Lucky' URL

        github.com
            -> https://github.com

        https://example.com
            -> https://example.com
    """

    destination = destination.strip()

    if not destination:
        return None


    # ---------------------------------
    # Already a complete URL
    # ---------------------------------

    if destination.startswith(
        "http://"
    ) or destination.startswith(
        "https://"
    ):

        return destination


    # ---------------------------------
    # Looks like a domain
    # ---------------------------------

    if "." in destination:

        return (
            "https://"
            + destination
        )


    # ---------------------------------
    # Natural website name
    #
    # Example:
    # YouTube
    # Spotify
    # Reddit
    #
    # Use Google's "I'm Feeling Lucky"
    # result so the browser redirects
    # directly to the most relevant website.
    # ---------------------------------

    encoded = quote_plus(
        destination
    )

    return (
        "https://www.google.com/search"
        f"?q={encoded}&btnI=1"
    )


def open_in_browser(
    url,
    browser_name
):

    # ---------------------------------
    # Default browser
    # ---------------------------------

    if browser_name.lower() == "default":

        webbrowser.open(
            url,
            new=2
        )

        return


    # ---------------------------------
    # Specific browser
    # ---------------------------------

    browsers = webbrowser._browsers

    selected = None

    for name, controller in browsers.items():

        if (
            browser_name.lower()
            in name.lower()
        ):

            selected = controller
            break


    # ---------------------------------
    # Browser wasn't already registered
    # ---------------------------------

    if selected is None:

        try:

            selected = webbrowser.get(
                browser_name
            )

        except Exception:

            # Try common Windows browser
            # executable registrations.

            browser_candidates = {
                "chrome": (
                    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                ),

                "edge": (
                    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
                ),

                "firefox": (
                    "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
                ),
            }

            executable = browser_candidates.get(
                browser_name.lower()
            )

            if not executable:

                raise RuntimeError(
                    f"Browser '{browser_name}' "
                    f"could not be found."
                )

            selected = webbrowser.BackgroundBrowser(
                executable
            )


    selected.open(
        url,
        new=2
    )


def execute(task):

    data = task.data or {}


    # ---------------------------------
    # Destination
    # ---------------------------------

    destination = (
        data.get("destination")
        or task.target
        or ""
    ).strip()


    # ---------------------------------
    # Browser
    # ---------------------------------

    browser_name = (
        data.get("browser")
        or "default"
    ).strip()


    if not destination:

        return ExecutionResult(
            handled=True,
            success=False,
            message=(
                "❌ No web destination specified."
            )
        )


    # ---------------------------------
    # Resolve destination into URL
    # ---------------------------------

    url = resolve_web_destination(
        destination
    )

    if url is None:

        return ExecutionResult(
            handled=True,
            success=False,
            message=(
                f"❌ I couldn't find a direct "
                f"website for '{destination}'."
            )
        )


    # ---------------------------------
    # Open browser
    # ---------------------------------

    try:

        status_print(
            f"🌐 Opening {destination}..."
        )

        open_in_browser(
            url,
            browser_name
        )

        success_print(
            f"{destination} opened."
        )

        return ExecutionResult(
            handled=True,
            success=True,
            data={
                "destination": destination,
                "url": url,
                "browser": browser_name
            }
        )


    except Exception as error:

        error_print(
            f"❌ Couldn't open "
            f"'{destination}'.\n"
            f"Reason: {error}"
        )

        return ExecutionResult(
            handled=True,
            success=False,
            data={
                "destination": destination,
                "url": url,
                "browser": browser_name,
                "error": str(error)
            }
        )