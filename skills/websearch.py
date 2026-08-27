from urllib.parse import quote_plus
import webbrowser


NAME = "Web Search"
INTENT = "search_web"

DESCRIPTION = (
    "Search the web or a specific website."
)


SEARCH_ENGINES = {
    "google": (
        "https://www.google.com/search?q={}"
    ),

    "bing": (
        "https://www.bing.com/search?q={}"
    ),

    "duckduckgo": (
        "https://duckduckgo.com/?q={}"
    ),
}


# ============================================================
# Website-native search
# ============================================================

SITE_SEARCH = {

    "reddit.com": (
        "https://www.reddit.com/search/?q={}"
    ),

    "github.com": (
        "https://github.com/search?q={}"
    ),

    "youtube.com": (
        "https://www.youtube.com/results?search_query={}"
    ),

    "wikipedia.org": (
        "https://en.wikipedia.org/w/index.php?search={}"
    ),

}


# ============================================================
# Clean website/domain
# ============================================================

def _clean_site(site):

    if not site:
        return None

    site = str(site).strip().lower()

    if not site:
        return None

    site = site.replace(
        "https://",
        ""
    )

    site = site.replace(
        "http://",
        ""
    )

    site = site.split(
        "/",
        1
    )[0]

    site = site.removeprefix(
        "www."
    )

    return site or None


# ============================================================
# Build search URL
# ============================================================

def _build_url(
    query,
    engine="google",
    site=None
):

    query = (
        query
        or ""
    ).strip()

    engine = (
        engine
        or "google"
    ).strip().lower()

    site = _clean_site(
        site
    )

    if not query:
        return None


    # --------------------------------------------------------
    # Website-native search
    #
    # Example:
    #
    # Search Reddit for Minecraft
    #
    # becomes:
    #
    # https://www.reddit.com/search/?q=Minecraft
    #
    # instead of:
    #
    # Google -> site:reddit.com Minecraft
    # --------------------------------------------------------

    if site:

        native_template = SITE_SEARCH.get(
            site
        )

        if native_template:

            return native_template.format(
                quote_plus(query)
            )


        # ----------------------------------------------------
        # Unknown website
        #
        # We don't know its native search URL,
        # so Google site-search is the safe fallback.
        # ----------------------------------------------------

        search_query = (
            f"site:{site} {query}"
        )

        encoded_query = quote_plus(
            search_query
        )

    else:

        encoded_query = quote_plus(
            query
        )


    template = SEARCH_ENGINES.get(
        engine,
        SEARCH_ENGINES["google"]
    )

    return template.format(
        encoded_query
    )


# ============================================================
# Open browser
# ============================================================

def _open_browser(
    url,
    browser="default"
):

    browser = (
        browser
        or "default"
    ).strip().lower()


    # --------------------------------------------------------
    # Default browser
    # --------------------------------------------------------

    if browser == "default":

        webbrowser.open(
            url
        )

        return


    # --------------------------------------------------------
    # Explicit browser
    # --------------------------------------------------------

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


    # Unknown browser:
    # Fall back to system default.

    webbrowser.open(
        url
    )


# ============================================================
# Execute
# ============================================================

def execute(task):

    data = task.data or {}


    # --------------------------------------------------------
    # Query
    # --------------------------------------------------------

    query = (
        data.get("query")
        or data.get("target")
        or task.target
        or ""
    ).strip()


    if not query:

        return (
            "What should I search for?"
        )


    # --------------------------------------------------------
    # Search engine
    # --------------------------------------------------------

    engine = (
        data.get("engine")
        or "google"
    ).strip().lower()


    # --------------------------------------------------------
    # Website
    # --------------------------------------------------------

    site = (
        data.get("site")
        or data.get("site_domain")
        or ""
    ).strip()


    # --------------------------------------------------------
    # Browser
    # --------------------------------------------------------

    browser = (
        data.get("browser")
        or "default"
    ).strip()


    # --------------------------------------------------------
    # Build URL
    # --------------------------------------------------------

    url = _build_url(
        query=query,
        engine=engine,
        site=site
    )


    if not url:

        return (
            "What should I search for?"
        )


    # --------------------------------------------------------
    # Open
    # --------------------------------------------------------

    try:

        _open_browser(
            url,
            browser
        )

    except Exception as error:

        return (
            "Couldn't perform web search. "
            f"Reason: {error}"
        )


    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    clean_site = _clean_site(
        site
    )


    if clean_site:

        return (
            f'Searching {clean_site} '
            f'for "{query}".'
        )


    return (
        f'Searching {engine.title()} '
        f'for "{query}".'
    )