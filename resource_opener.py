import os
from pathlib import Path


class ResourceOpener:

    def open(
        self,
        path
    ):

        if not path:

            return {
                "success": False,
                "message": (
                    "No resource path was supplied."
                ),
            }

        path = Path(
            os.path.expandvars(
                str(path)
            )
        ).expanduser()

        try:

            path = path.resolve()

        except OSError as error:

            return {
                "success": False,
                "message": (
                    f"I couldn't resolve "
                    f"'{path}': {error}"
                ),
            }


        if not path.exists():

            return {
                "success": False,
                "message": (
                    f"I couldn't find "
                    f"'{path}'."
                ),
                "path": str(path),
            }


        try:

            os.startfile(
                str(path)
            )

            return {
                "success": True,
                "action": "open_resource",
                "path": str(path),
                "resource_type": (
                    self._resource_type(path)
                ),
                "message": (
                    f"Opened '{path.name}'."
                ),
            }

        except Exception as error:

            return {
                "success": False,
                "action": "open_resource",
                "path": str(path),
                "message": (
                    f"I found '{path}', but "
                    f"Windows couldn't open it: "
                    f"{error}"
                ),
            }


    def _resource_type(
        self,
        path
    ):

        suffix = path.suffix.lower()

        if suffix in {
            ".py", ".ts", ".tsx",
            ".js", ".jsx",
            ".html", ".css",
            ".scss", ".rs",
            ".java", ".c",
            ".cpp", ".h",
            ".hpp", ".sql",
        }:

            return "code"

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


resource_opener = ResourceOpener()