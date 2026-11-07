class ClickDetector:
    def __init__(self, confirmation_frames=3, release_frames=5):
        self.confirmation_frames = confirmation_frames
        self.release_frames = release_frames
        self.active = False
        self.pinch_count = 0
        self.release_count = 0

    def update(self, gesture):
        if gesture == "PINCH":
            self.pinch_count += 1
            self.release_count = 0

            if self.pinch_count >= self.confirmation_frames and not self.active:
                self.active = True
                return True
        else:
            self.pinch_count = 0
            self.release_count += 1

            if self.release_count >= self.release_frames:
                self.active = False

        return False