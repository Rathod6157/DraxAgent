import re
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


COMMON_TLDS = (
    ".com",
    ".org",
    ".net",
    ".io",
    ".dev",
    ".co",
    ".app",
)


def normalize_name(name: str) -> str:
    """
    Convert a natural website name into a domain-friendly slug.

    Examples:
        "YouTube" -> "youtube"
        "Open GitHub" -> "github"
        "Discord Website" -> "discord"
    """

    value = name.strip().lower()

    value = re.sub(
        r"\b(website|web|site|homepage|home page)\b",
        "",
        value,
    )

    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value,
    )

    value = value.strip()

    return value.replace(" ", "")


def is_url(value: str) -> bool:
    return value.startswith(
        ("http://", "https://")
    )


def looks_like_domain(value: str) -> bool:
    return "." in value and " " not in value


def check_url(url: str) -> bool:
    """
    Check whether a URL is reachable.

    We don't download the page body.
    """

    try:

        request = Request(
            url,
            method="HEAD",
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )

        with urlopen(
            request,
            timeout=4,
        ) as response:

            return (
                200
                <= response.status
                < 500
            )

    except HTTPError as error:

        # A 3xx/4xx response can still mean
        # that the domain itself exists.
        return error.code < 500

    except (
        URLError,
        TimeoutError,
        OSError,
    ):

        return False


def resolve_web_destination(
    destination: str,
) -> str | None:

    value = destination.strip()

    if not value:
        return None

    # ---------------------------------
    # Already a full URL
    # ---------------------------------

    if is_url(value):

        return value


    # ---------------------------------
    # Already looks like a domain
    # ---------------------------------

    if looks_like_domain(value):

        return (
            "https://"
            + value
        )


    # ---------------------------------
    # Natural website name
    # ---------------------------------

    slug = normalize_name(value)

    if not slug:
        return None


    # ---------------------------------
    # Try likely domains
    # ---------------------------------

    candidates = []

    for tld in COMMON_TLDS:

        candidates.append(
            f"https://{slug}{tld}"
        )


    for url in candidates:

        if check_url(url):

            return url


    # ---------------------------------
    # Could not confidently resolve
    # ---------------------------------

    return None