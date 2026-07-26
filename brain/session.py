class SessionEngine:

    def detect(
        self,
        observation
    ):

        activity = observation.get(
            "activity",
            "Unknown"
        )

        duration = observation.get(
            "window_duration",
            0
        )

        recent = observation.get(
            "recent",
            []
        )

        confidence = 50

        session = activity

        if activity == "Coding":

            confidence = 95

        elif activity == "Browsing":

            confidence = 80

        elif activity == "Gaming":

            confidence = 95

        elif activity == "Music":

            confidence = 90

        elif activity == "Unknown":

            confidence = 20

        return {

            "type": session,

            "confidence": confidence,

            "duration": duration,

            "recent": recent
        }


session_engine = SessionEngine()