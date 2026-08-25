import webbrowser

from terminal import (
    status_print,
    success_print,
    error_print,
)

from brain.execution_result import (
    ExecutionResult
)


NAME = "Open Web"
INTENT = "open_web"
DESCRIPTION = "Opens websites and web destinations."
VERSION = "1.0"
AUTHOR = "Harshith"


def execute(task):

    data = task.data or {}

    destination = (
        data.get("destination")
        or task.target
        or ""
    ).strip()

    browser_name = (
        data.get("browser")
        or "default"
    ).strip()


    if not destination:

        return ExecutionResult(
            handled=True,
            success=False,
            message="❌ No web destination specified."
        )


    # ---------------------------------
    # Convert destination into URL
    # ---------------------------------

    if not (
        destination.startswith(
            "http://"
        )
        or destination.startswith(
            "https://"
        )
    ):

        if "." in destination:

            url = (
                "https://"
                + destination
            )

        else:

            # Let the browser/search engine
            # resolve natural destinations.
            url = (
                "https://www.google.com/search?q="
                + destination.replace(
                    " ",
                    "+"
                )
            )

    else:

        url = destination


    # ---------------------------------
    # Browser selection
    # ---------------------------------

    try:

        if browser_name.lower() == "default":

            webbrowser.open(
                url,
                new=2
            )

        else:

            browsers = (
                webbrowser._browsers
            )

            selected = None

            for name, controller in browsers.items():

                if (
                    browser_name.lower()
                    in name.lower()
                ):

                    selected = controller

                    break

            if selected is None:

                # Try Windows browser lookup
                selected = (
                    webbrowser.get(
                        browser_name
                    )
                )

            selected.open(
                url,
                new=2
            )


        status_print(
            f"🌐 Opening {destination}..."
        )

        success_print(
            f"{destination} opened."
        )

        return ExecutionResult(
            handled=True,
            success=True
        )


    except Exception as error:

        error_print(
            f"❌ Couldn't open "
            f"'{destination}'.\n"
            f"Reason: {error}"
        )

        return ExecutionResult(
            handled=True,
            success=False
        )