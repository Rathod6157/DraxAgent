from urllib.parse import quote_plus
import webbrowser


NAME = "Web Search"
INTENT = "search_web"

DESCRIPTION = (
    "Search the web or a specific website."
)


# General search engines
SEARCH_ENGINES = {
    "google": "https://www.google.com/search?q={}",
    "bing": "https://www.bing.com/search?q={}",
    "duckduckgo": "https://duckduckgo.com/?q={}",
}


# Site-specific search destinations
SEARCH_SITES = {
    "youtube": (
        "https://www.youtube.com/results?search_query={}"
    ),

    "reddit": (
        "https://www.reddit.com/search/?q={}"
    ),

    "github": (
        "https://github.com/search?q={}"
    ),

    "stackoverflow": (
        "https://stackoverflow.com/search?q={}"
    ),

    "wikipedia": (
        "https://en.wikipedia.org/w/index.php?search={}"
    ),

    "amazon": (
        "https://www.amazon.com/s?k={}"
    ),

    "quora": (
        "https://www.quora.com/search?q={}"
    ),
}


def _build_url(
    query,
    engine="google",
    site=None
):

    encoded_query = quote_plus(
        query
    )

    site = (
        site
        or ""
    ).lower().strip()

    engine = (
        engine
        or "google"
    ).lower().strip()

    # Site-specific search has priority.
    if site in SEARCH_SITES:

        return SEARCH_SITES[
            site
        ].format(
            encoded_query
        )

    # Otherwise use the requested general search engine.
    template = SEARCH_ENGINES.get(
        engine,
        SEARCH_ENGINES["google"]
    )

    return template.format(
        encoded_query
    )


def _open_browser(
    url,
    browser
):

    browser = (
        browser
        or "default"
    ).strip().lower()

    if browser == "default":

        webbrowser.open(
            url
        )

        return

    browser_map = {

        "chrome": (
            "C:/Program Files/Google/"
            "Chrome/Application/chrome.exe"
        ),

        "edge": (
            "C:/Program Files (x86)/Microsoft/"
            "Edge/Application/msedge.exe"
        ),

        "firefox": (
            "C:/Program Files/Mozilla Firefox/"
            "firefox.exe"
        ),
    }

    executable = browser_map.get(
        browser
    )

    if executable:

        controller = (
            webbrowser.BackgroundBrowser(
                executable
            )
        )

        controller.open(
            url
        )

        return

    # Unknown browser -> system default.
    webbrowser.open(
        url
    )


def execute(task):

    data = task.data or {}

    query = (
        data.get("query")
        or task.target
        or ""
    ).strip()

    engine = (
        data.get("engine")
        or "google"
    ).strip().lower()

    site = (
        data.get("site")
        or ""
    ).strip().lower()

    browser = (
        data.get("browser")
        or "default"
    ).strip()

    if not query:

        return (
            "What should I search for?"
        )

    url = _build_url(
        query=query,
        engine=engine,
        site=site
    )

    try:

        _open_browser(
            url,
            browser
        )

        if site:

            return (
                f'Searching {site.title()} '
                f'for "{query}".'
            )

        return (
            f'Searching {engine.title()} '
            f'for "{query}".'
        )

    except Exception as error:

        return (
            "Couldn't perform web search. "
            f"Reason: {error}"
        )