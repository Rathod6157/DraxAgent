class Experience:

    def __init__(self):

        self.sessions = []

    def add(
        self,
        session
    ):

        self.sessions.append(session)

        self.sessions = self.sessions[-30:]

    def recent(
        self
    ):

        return self.sessions

    def latest(
        self
    ):

        if not self.sessions:
            return None

        return self.sessions[-1]


experience = Experience()