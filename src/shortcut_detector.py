import time

class ShortcutDetector:
    def __init__(self, hold_duration=0.5):
        self.hold_duration = hold_duration
        self.hold_start = None
        self.current_gesture = None
        self.triggered = False

    def update(self, gesture):
        if gesture not in ("THREE_FINGERS", "COPY", "PASTE"):
            self.reset()
            return None

        if gesture != self.current_gesture:
            self.current_gesture = gesture
            self.hold_start = time.monotonic()
            self.triggered = False
            return None

        if self.triggered:
            return None

        if time.monotonic() - self.hold_start >= self.hold_duration:
            self.triggered = True

            if gesture == "THREE_FINGERS":
                return "ALT_TAB"
            if gesture == "COPY":
                return "COPY"
            if gesture == "PASTE":
                return "PASTE"

        return None

    def reset(self):
        self.hold_start = None
        self.current_gesture = None
        self.triggered = False