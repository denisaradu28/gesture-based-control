class ClickDetector:
    def __init__(self):
        self.armed = False
        self.dragging = False

    def update(self, gesture):
        if self.dragging:
            if gesture != "FIST":
                self.dragging = False
                self.armed = False
                return "DRAG_END"
            return None

        if gesture == "V_MOVE":
            self.armed = True
            return None

        if gesture in ("COPY", "PASTE", "THREE_FINGERS", "SCROLL", "OPEN_PALM", "NONE"):
            return None

        if gesture in ("NONE", "OPEN_PALM", "SCROLL", "THREE_FINGERS", "COPY", "PASTE"):
            self.armed = False
            return None

        if not self.armed:
            return None

        self.armed = False

        if gesture == "LEFT_CLICK_GESTURE":
            return "SINGLE_CLICK"

        if gesture == "RIGHT_CLICK_GESTURE":
            return "RIGHT_CLICK"

        if gesture == "V_CLOSED":
            return "DOUBLE_CLICK"

        if gesture == "FIST":
            self.dragging = True
            return "DRAG_START"

        return None

    def reset(self):
        self.armed = False
        self.dragging = False