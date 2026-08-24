import json
import threading
from collections import OrderedDict

from brain.router import router
from brain.intelligence.activity_prompt import (
    build_activity_prompt
)


class ActivityClassifier:

    CACHE_SIZE = 128

    DEBOUNCE_SECONDS = 1.5


    def __init__(self):

        self.cache = OrderedDict()

        self.lock = threading.Lock()

        self.timer = None

        self.generation = 0


    # ---------------------------------
    # Public entry point
    # ---------------------------------

    def classify_async(
        self,
        context_data,
        callback
    ):

        with self.lock:

            self.generation += 1

            generation = self.generation


            if self.timer:

                self.timer.cancel()


            self.timer = threading.Timer(
                self.DEBOUNCE_SECONDS,
                self._classify,
                args=(
                    context_data,
                    callback,
                    generation
                )
            )

            self.timer.daemon = True

            self.timer.start()


    # ---------------------------------
    # Classification
    # ---------------------------------

    def _classify(
        self,
        context_data,
        callback,
        generation
    ):

        # ---------------------------------
        # Ignore stale debounce calls
        # ---------------------------------

        with self.lock:

            if generation != self.generation:

                return


        # ---------------------------------
        # Cache
        # ---------------------------------

        cache_key = self._cache_key(
            context_data
        )


        with self.lock:

            if cache_key in self.cache:

                result = self.cache.pop(
                    cache_key
                )

                # Move to most-recent position.
                self.cache[cache_key] = result

                callback(result)

                return


        # ---------------------------------
        # Ask Gemini
        # ---------------------------------

        prompt = build_activity_prompt(
            context_data
        )

        raw_response = router.reason(
            prompt
        )


        result = self._parse(
            raw_response
        )


        # ---------------------------------
        # Store in LRU cache
        # ---------------------------------

        with self.lock:

            self.cache[cache_key] = result

            self.cache.move_to_end(
                cache_key
            )


            while len(self.cache) > self.CACHE_SIZE:

                self.cache.popitem(
                    last=False
                )


        # ---------------------------------
        # Deliver result
        # ---------------------------------

        callback(result)


    # ---------------------------------
    # Cache key
    # ---------------------------------

    def _cache_key(
        self,
        data
    ):

        return (
            str(
                data.get("application")
                or ""
            ).strip().lower(),

            str(
                data.get("process")
                or ""
            ).strip().lower(),

            str(
                data.get("executable")
                or ""
            ).strip().lower(),

            str(
                data.get("window_title")
                or ""
            ).strip().lower(),
        )


    # ---------------------------------
    # Parse Gemini response
    # ---------------------------------

    def _parse(
        self,
        raw_response
    ):

        try:

            data = json.loads(
                raw_response
            )


            activity_name = str(
                data.get(
                    "activity",
                    "Unknown"
                )
            ).strip()


            confidence = int(
                data.get(
                    "confidence",
                    20
                )
            )


            confidence = max(
                0,
                min(
                    confidence,
                    100
                )
            )


            if not activity_name:

                activity_name = "Unknown"


            return {
                "activity": activity_name,
                "confidence": confidence
            }


        except Exception:

            return {
                "activity": "Unknown",
                "confidence": 20
            }


activity_classifier = ActivityClassifier()