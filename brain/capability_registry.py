from dataclasses import dataclass, asdict
from typing import Callable, Optional


@dataclass(frozen=True)
class Capability:

    name: str

    description: str

    category: str

    requires_confirmation: bool = False

    destructive: bool = False

    handler: Optional[Callable] = None

    def public(self):

        data = asdict(self)

        # Functions are implementation details and must never
        # be exposed to the language model.
        data.pop(
            "handler",
            None
        )

        return data


class CapabilityRegistry:

    def __init__(self):

        self._capabilities = {}


    # =========================================================
    # REGISTER
    # =========================================================

    def register(
        self,
        name,
        description,
        category,
        handler=None,
        requires_confirmation=False,
        destructive=False,
    ):

        name = str(
            name
        ).strip()

        if not name:
            raise ValueError(
                "Capability name cannot be empty."
            )

        capability = Capability(
            name=name,
            description=str(
                description
            ).strip(),
            category=str(
                category
            ).strip(),
            requires_confirmation=bool(
                requires_confirmation
            ),
            destructive=bool(
                destructive
            ),
            handler=handler,
        )

        self._capabilities[
            name
        ] = capability

        return capability


    # =========================================================
    # GET
    # =========================================================

    def get(
        self,
        name
    ):

        return self._capabilities.get(
            str(name).strip()
        )


    # =========================================================
    # HAS
    # =========================================================

    def has(
        self,
        name
    ):

        return (
            self.get(name)
            is not None
        )


    # =========================================================
    # ALL
    # =========================================================

    def all(
        self
    ):

        return list(
            self._capabilities.values()
        )


    # =========================================================
    # PUBLIC DESCRIPTION
    # =========================================================

    def describe(
        self
    ):

        return [
            capability.public()
            for capability
            in self.all()
        ]


    # =========================================================
    # CATEGORIES
    # =========================================================

    def categories(
        self
    ):

        result = {}

        for capability in self.all():

            result.setdefault(
                capability.category,
                []
            ).append(
                capability.name
            )

        return result


    # =========================================================
    # EXECUTE
    # =========================================================

    def execute(
        self,
        name,
        *args,
        **kwargs
    ):

        capability = self.get(
            name
        )

        if capability is None:

            return {
                "success": False,
                "error": (
                    f"Unknown capability: {name}"
                )
            }

        if capability.handler is None:

            return {
                "success": False,
                "error": (
                    f"Capability '{name}' "
                    "has no handler."
                )
            }

        try:

            return capability.handler(
                *args,
                **kwargs
            )

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }


# =============================================================
# SHARED REGISTRY
# =============================================================

capabilities = CapabilityRegistry()


# =============================================================
# CORE CAPABILITIES
# =============================================================

capabilities.register(
    name="observe_desktop",
    description=(
        "Observe the current desktop, foreground application, "
        "window, and visible computer state."
    ),
    category="observation",
)

capabilities.register(
    name="search_files",
    description=(
        "Find local files and resources on the computer."
    ),
    category="resources",
)

capabilities.register(
    name="inspect_file",
    description=(
        "Read and inspect a local file and relevant related files."
    ),
    category="resources",
)

capabilities.register(
    name="open_resource",
    description=(
        "Open a local file or resource using Windows' "
        "associated application."
    ),
    category="resources",
)

capabilities.register(
    name="open_app",
    description=(
        "Launch a desktop application."
    ),
    category="applications",
)

capabilities.register(
    name="close_app",
    description=(
        "Close a desktop application."
    ),
    category="applications",
    requires_confirmation=True,
)

capabilities.register(
    name="app_status",
    description=(
        "Check whether an application is open, running, "
        "responding, or not responding."
    ),
    category="applications",
)

capabilities.register(
    name="watch_app",
    description=(
        "Watch an application and report when its state changes."
    ),
    category="monitoring",
)

capabilities.register(
    name="search_web",
    description=(
        "Search the web for information or online resources."
    ),
    category="web",
)

capabilities.register(
    name="open_web",
    description=(
        "Open a website or web destination."
    ),
    category="web",
)

capabilities.register(
    name="click",
    description=(
        "Click a visible element on the desktop."
    ),
    category="computer_control",
)

capabilities.register(
    name="type",
    description=(
        "Type text into the active desktop application."
    ),
    category="computer_control",
)

capabilities.register(
    name="wait",
    description=(
        "Wait for the desktop or an application to react."
    ),
    category="computer_control",
)

capabilities.register(
    name="verify",
    description=(
        "Verify whether a requested desktop action actually "
        "produced the expected result."
    ),
    category="verification",
)

capabilities.register(
    name="edit_file",
    description=(
        "Modify a local file after the requested change is "
        "understood and permitted."
    ),
    category="resources",
    requires_confirmation=True,
    destructive=True,
)