class GestureStabilizer:
    def __init__(self, confirmation_frames=5):
        self.confirmation_frames = confirmation_frames
        self.stable_gesture = "NONE"
        self.previous_gesture = "NONE"
        self.frame_count = 0

    def update(self, gesture):
        if gesture == self.previous_gesture:
            self.frame_count += 1
        else:
            self.previous_gesture = gesture
            self.frame_count = 1

        if self.frame_count >= self.confirmation_frames:
            self.stable_gesture = gesture

        return self.stable_gesture

    def reset(self):
        self.stable_gesture = "NONE"
        self.previous_gesture = "NONE"
        self.frame_count = 0