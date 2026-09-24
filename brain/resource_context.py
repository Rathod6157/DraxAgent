import re
from pathlib import Path


# =============================================================
# RESOURCE EXTENSIONS
# =============================================================

RESOURCE_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
    ".ini",
    ".cfg",
    ".rs",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".sql",
    ".xml",
    ".sh",
    ".ps1",
    ".bat",
    ".cmd",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
}


class ResourceContext:

    # =========================================================
    # EXTRACT FILENAME FROM WINDOW TITLE
    # =========================================================

    def filename_from_window(
        self,
        window_title
    ):

        title = str(
            window_title or ""
        ).strip()

        if not title:
            return None

        # -----------------------------------------------------
        # First try a normal filename-like token.
        # -----------------------------------------------------

        pattern = (
            r"([A-Za-z0-9_.()\-\[\] ]+"
            r"\.(?:"
            r"py|ts|tsx|js|jsx|html|css|scss|"
            r"json|toml|yaml|yml|md|txt|ini|cfg|"
            r"rs|java|c|cpp|h|hpp|sql|xml|"
            r"sh|ps1|bat|cmd|pdf|doc|docx|"
            r"xls|xlsx|ppt|pptx|png|jpg|jpeg|"
            r"gif|webp|svg"
            r"))\b"
        )

        match = re.search(
            pattern,
            title,
            flags=re.IGNORECASE
        )

        if match:

            return (
                match.group(1)
                .strip()
            )

        return None


    # =========================================================
    # RESOURCE TYPE
    # =========================================================

    def resource_type(
        self,
        path
    ):

        if not path:
            return "unknown"

        suffix = Path(
            str(path)
        ).suffix.lower()

        if suffix in {
            ".py",
            ".ts",
            ".tsx",
            ".js",
            ".jsx",
            ".html",
            ".css",
            ".scss",
            ".rs",
            ".java",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".sql",
            ".sh",
            ".ps1",
            ".bat",
            ".cmd",
        }:

            return "code"

        if suffix in {
            ".md",
            ".txt",
            ".ini",
            ".cfg",
            ".json",
            ".toml",
            ".yaml",
            ".yml",
            ".xml",
        }:

            return "text"

        if suffix in {
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
        }:

            return "document"

        if suffix in {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
            ".svg",
        }:

            return "image"

        return "file"


    # =========================================================
    # BUILD CONTEXT
    # =========================================================

    def build(
        self,
        application=None,
        process=None,
        window=None
    ):

        filename = (
            self.filename_from_window(
                window
            )
        )

        return {

            "current_resource": {
                "name": filename,
                "type": (
                    self.resource_type(
                        filename
                    )
                    if filename
                    else "unknown"
                ),
            },

            "foreground_application": (
                application
                or "Unknown application"
            ),

            "foreground_process": (
                process
                or ""
            ),

            "window": (
                window
                or ""
            ),

        }


resource_context = ResourceContext()