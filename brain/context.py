import time


class Context:

    def __init__(self):

        # ---------------------------------
        # Current window
        # ---------------------------------

        self.current_window = None

        self.current_hwnd = None

        self.current_pid = None

        self.current_process = None

        self.current_executable = None

        self.current_application = None


        # ---------------------------------
        # Previous window
        # ---------------------------------

        self.previous_window = None

        self.previous_hwnd = None

        self.previous_pid = None

        self.previous_process = None

        self.previous_application = None


        # ---------------------------------
        # Timing
        # ---------------------------------

        self.window_started = time.time()

        self.last_activity = time.time()

        self.current_task = None


    def set_window(
        self,
        title,
        hwnd=None,
        application=None,
        process=None,
        executable=None,
        pid=None
    ):

        # ---------------------------------
        # Same actual window?
        # ---------------------------------

        if (
            hwnd == self.current_hwnd
            and pid == self.current_pid
        ):

            # The title may change while the
            # same window remains active.
            self.current_window = title

            return


        # ---------------------------------
        # Preserve previous window
        # ---------------------------------

        self.previous_window = (
            self.current_window
        )

        self.previous_hwnd = (
            self.current_hwnd
        )

        self.previous_pid = (
            self.current_pid
        )

        self.previous_process = (
            self.current_process
        )

        self.previous_application = (
            self.current_application
        )


        # ---------------------------------
        # Store current window
        # ---------------------------------

        self.current_window = title

        self.current_hwnd = hwnd

        self.current_pid = pid

        self.current_process = process

        self.current_executable = executable

        self.current_application = application


        # ---------------------------------
        # Reset duration
        # ---------------------------------

        self.window_started = time.time()


    @property
    def window_duration(self):

        return int(
            time.time()
            - self.window_started
        )


context = Context()