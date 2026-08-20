class ExecutionResult:

    def __init__(
        self,
        handled=False,
        success=False,
        message="",
        data=None,
        exit_requested=False
    ):

        self.handled = handled
        self.success = success
        self.message = message
        self.data = data or {}
        self.exit_requested = exit_requested