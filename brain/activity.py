import time


class Activity:

    def __init__(self):

        self.name = "Unknown"

        self.confidence = 0

        self.windows = []

        # ---------------------------------
        # Application responsible for activity
        # ---------------------------------

        self.application = None

        self.process = None

        # ---------------------------------
        # Activity timing
        # ---------------------------------

        self.started_at = time.time()


    def update(
        self,
        name,
        confidence,
        windows,
        application=None,
        process=None
    ):

        # ---------------------------------
        # Detect actual activity change
        # ---------------------------------

        activity_changed = (
            name != self.name
            or application != self.application
            or process != self.process
        )


        # ---------------------------------
        # Reset timer only when the actual
        # tracked activity changes.
        #
        # Opening/focusing DraxAgent will
        # never reach this function because
        # ActivityEngine ignores DraxAgent.
        # ---------------------------------

        if activity_changed:

            self.started_at = time.time()


        # ---------------------------------
        # Store activity
        # ---------------------------------

        self.name = name

        self.confidence = confidence

        self.windows = windows

        self.application = application

        self.process = process


activity = Activity()