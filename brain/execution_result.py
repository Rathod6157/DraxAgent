class ExecutionResult:

    def __init__(
        self,
        handled=False,
        success=False,
        message="",
        data=None
    ):

        self.handled = handled
        self.success = success
        self.message = message
        self.data = data or {}