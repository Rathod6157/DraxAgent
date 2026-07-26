class Activity:

    def __init__(self):

        self.name = "Unknown"

        self.confidence = 0

        self.windows = []

    def update(
        self,
        name,
        confidence,
        windows
    ):

        self.name = name

        self.confidence = confidence

        self.windows = windows


activity = Activity()