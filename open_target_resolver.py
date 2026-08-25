from resolver import resolve_application


def resolve_open_target(
    target,
    ai_intent
):

    target = (
        target
        or ""
    ).strip()

    if not target:

        return {
            "status": "not_found",
            "target": target,
            "intent": ai_intent,
            "app_match": None
        }

    app_results = resolve_application(
        target,
        limit=3
    )

    # -----------------------------------------
    # Determine whether a local application
    # actually exists.
    # -----------------------------------------

    valid_apps = [
        app
        for app in app_results
        if app["score"] >= 0.70
    ]

    best_app = (
        valid_apps[0]
        if valid_apps
        else None
    )

    # -----------------------------------------
    # AI thinks this is an application
    # -----------------------------------------

    if ai_intent == "open_app":

        if best_app:

            # Very strong local match.
            if best_app["score"] >= 0.95:

                return {
                    "status": "app",
                    "target": target,
                    "intent": "open_app",
                    "app_match": best_app
                }

            # Local app exists, but match isn't
            # completely certain.
            return {
                "status": "app_confirm",
                "target": target,
                "intent": "open_app",
                "app_match": best_app
            }

        # AI thought app, but machine doesn't
        # have a matching application.
        #
        # Let web handling take over.
        return {
            "status": "web_fallback",
            "target": target,
            "intent": "open_web",
            "app_match": None
        }

    # -----------------------------------------
    # AI thinks this is a website
    # -----------------------------------------

    if ai_intent == "open_web":

        if best_app:

            # Strong local app match means we have
            # a genuine app-vs-web conflict.
            if best_app["score"] >= 0.95:

                return {
                    "status": "app_or_web",
                    "target": target,
                    "intent": "open_web",
                    "app_match": best_app
                }

        # No strong local application.
        return {
            "status": "web",
            "target": target,
            "intent": "open_web",
            "app_match": None
        }

    # -----------------------------------------
    # Unknown open intent
    # -----------------------------------------

    return {
        "status": "unknown",
        "target": target,
        "intent": ai_intent,
        "app_match": best_app
    }