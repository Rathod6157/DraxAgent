import hashlib
import json
import os
import tempfile
import threading
from collections import OrderedDict

from PIL import ImageGrab

from brain.router import router
from brain.screen_vision import vision
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

    # ============================================================
    # PUBLIC
    # ============================================================

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

    # ============================================================
    # CLASSIFICATION
    # ============================================================

    def _classify(
        self,
        context_data,
        callback,
        generation
    ):

        # --------------------------------------------------------
        # Ignore stale requests
        # --------------------------------------------------------

        if not self._is_current(
            generation
        ):

            return

        screenshot_path = None

        visual_context = None

        try:

            # ----------------------------------------------------
            # ONE SCREENSHOT
            # ----------------------------------------------------

            screenshot_path = (
                self._capture_screen()
            )

            if not self._is_current(
                generation
            ):

                return

            # ----------------------------------------------------
            # VISUAL PERCEPTION
            # ----------------------------------------------------

            visual_result = vision.analyze(
                screenshot_path,
                instruction="""
Analyze this desktop screenshot specifically for
USER ACTIVITY CLASSIFICATION.

Determine what the user is actually doing RIGHT NOW.

Pay special attention to:

- the main visible application
- whether a video is actually playing
- whether a website is showing a homepage/feed
- articles or documents being read
- code editors
- terminals
- documentation
- search results
- games
- media players
- writing/editing interfaces
- development tools
- visible dialogs or overlays

IMPORTANT:

Do NOT assume that seeing YouTube means the user is
watching a video.

YouTube homepage / recommendations / subscriptions
→ browsing YouTube

YouTube search results
→ searching YouTube

YouTube video player visibly showing a video
→ watching video

Likewise:

A browser does NOT automatically mean browsing.

Visual Studio Code does NOT automatically mean coding.

Use the actual visible content as evidence.

Return the normal ScreenVision JSON structure.
""",
            )

            if (
                isinstance(
                    visual_result,
                    dict
                )
                and visual_result.get(
                    "success"
                )
            ):

                visual_context = (
                    visual_result.get(
                        "vision"
                    )
                )

            # ----------------------------------------------------
            # BUILD CONTEXT
            # ----------------------------------------------------

            enriched_context = dict(
                context_data
            )

            if visual_context:

                enriched_context[
                    "visual_context"
                ] = visual_context

            # ----------------------------------------------------
            # VISUAL CACHE
            # ----------------------------------------------------

            cache_key = (
                self._cache_key(
                    enriched_context
                )
            )

            with self.lock:

                cached = self.cache.get(
                    cache_key
                )

                if cached is not None:

                    self.cache.move_to_end(
                        cache_key
                    )

                    callback(
                        cached
                    )

                    return

            # ----------------------------------------------------
            # CLASSIFY
            # ----------------------------------------------------

            prompt = build_activity_prompt(
                enriched_context
            )

            raw_response = router.reason(
                prompt
            )

            result = self._parse(
                raw_response
            )

            # ----------------------------------------------------
            # STORE
            # ----------------------------------------------------

            with self.lock:

                self.cache[
                    cache_key
                ] = result

                self.cache.move_to_end(
                    cache_key
                )

                while (
                    len(self.cache)
                    > self.CACHE_SIZE
                ):

                    self.cache.popitem(
                        last=False
                    )

            # ----------------------------------------------------
            # DELIVER
            # ----------------------------------------------------

            if self._is_current(
                generation
            ):

                callback(
                    result
                )

        except Exception as exc:

            print(
                "[ActivityClassifier] "
                f"Classification failed: {exc}"
            )

            # ----------------------------------------------------
            # Metadata-only fallback
            # ----------------------------------------------------

            try:

                fallback_context = dict(
                    context_data
                )

                prompt = build_activity_prompt(
                    fallback_context
                )

                raw_response = router.reason(
                    prompt
                )

                result = self._parse(
                    raw_response
                )

            except Exception as fallback_exc:

                print(
                    "[ActivityClassifier] "
                    f"Fallback failed: {fallback_exc}"
                )

                result = {
                    "activity": "Unknown",
                    "confidence": 20
                }

            if self._is_current(
                generation
            ):

                callback(
                    result
                )

        finally:

            # ----------------------------------------------------
            # DELETE TEMPORARY SCREENSHOT
            # ----------------------------------------------------

            if screenshot_path:

                try:

                    os.remove(
                        screenshot_path
                    )

                except OSError:

                    pass

    # ============================================================
    # SCREEN CAPTURE
    # ============================================================

    def _capture_screen(
        self
    ):

        screenshot = ImageGrab.grab(
            all_screens=True
        )

        temp_file = tempfile.NamedTemporaryFile(
            prefix="drax_activity_",
            suffix=".png",
            delete=False
        )

        path = temp_file.name

        temp_file.close()

        screenshot.save(
            path,
            "PNG"
        )

        return path

    # ============================================================
    # CURRENT REQUEST CHECK
    # ============================================================

    def _is_current(
        self,
        generation
    ):

        with self.lock:

            return (
                generation
                == self.generation
            )

    # ============================================================
    # CACHE KEY
    # ============================================================

    def _cache_key(
        self,
        data
    ):

        visual = (
            data.get(
                "visual_context"
            )
            or {}
        )

        # --------------------------------------------------------
        # Metadata
        # --------------------------------------------------------

        application = str(
            data.get(
                "application"
            )
            or ""
        ).strip().lower()

        process = str(
            data.get(
                "process"
            )
            or ""
        ).strip().lower()

        executable = str(
            data.get(
                "executable"
            )
            or ""
        ).strip().lower()

        window_title = str(
            data.get(
                "window_title"
            )
            or ""
        ).strip().lower()

        # --------------------------------------------------------
        # Visual summary
        # --------------------------------------------------------

        summary = str(
            visual.get(
                "summary"
            )
            or ""
        ).strip().lower()

        visual_application = str(
            visual.get(
                "application"
            )
            or ""
        ).strip().lower()

        # --------------------------------------------------------
        # Important visible text
        # --------------------------------------------------------

        text = visual.get(
            "text"
        ) or []

        if isinstance(
            text,
            list
        ):

            text = [
                str(item).strip().lower()
                for item in text
                if str(item).strip()
            ]

        else:

            text = [
                str(text).strip().lower()
            ]

        text = text[:20]

        # --------------------------------------------------------
        # Visible element labels
        #
        # We deliberately ignore coordinates.
        # A tiny window movement should not create a new
        # activity state.
        # --------------------------------------------------------

        elements = visual.get(
            "elements"
        ) or []

        element_signals = []

        if isinstance(
            elements,
            list
        ):

            for element in elements[:40]:

                if not isinstance(
                    element,
                    dict
                ):

                    continue

                label = str(
                    element.get(
                        "label"
                    )
                    or ""
                ).strip().lower()

                element_type = str(
                    element.get(
                        "type"
                    )
                    or ""
                ).strip().lower()

                if label:

                    element_signals.append(
                        f"{element_type}:{label}"
                    )

        # --------------------------------------------------------
        # Stable visual payload
        # --------------------------------------------------------

        visual_payload = {
            "summary": summary,
            "application": visual_application,
            "text": text,
            "elements": element_signals,
        }

        visual_blob = json.dumps(
            visual_payload,
            sort_keys=True,
            ensure_ascii=False
        )

        visual_hash = hashlib.sha256(
            visual_blob.encode(
                "utf-8"
            )
        ).hexdigest()

        return (
            application,
            process,
            executable,
            window_title,
            visual_hash,
        )

    # ============================================================
    # RESPONSE PARSER
    # ============================================================

    def _parse(
        self,
        raw_response
    ):

        try:

            if isinstance(
                raw_response,
                dict
            ):

                data = raw_response

            else:

                text = str(
                    raw_response
                ).strip()

                # --------------------------------------------
                # Remove accidental markdown fences
                # --------------------------------------------

                if text.startswith(
                    "```"
                ):

                    text = text.replace(
                        "```json",
                        ""
                    )

                    text = text.replace(
                        "```",
                        ""
                    )

                    text = text.strip()

                data = json.loads(
                    text
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

        except Exception as exc:

            print(
                "[ActivityClassifier] "
                f"Could not parse response: {exc}"
            )

            return {
                "activity": "Unknown",
                "confidence": 20
            }


activity_classifier = ActivityClassifier()