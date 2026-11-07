from collections import deque, Counter

class GestureStabilizer:
    def __init__(self, window_size=7, min_count=5):
        self.history = deque(maxlen=window_size)
        self.min_count = min_count
        self.stable_gesture = "NONE"

    def update(self, gesture):
        self.history.append(gesture)

        counts = Counter(self.history)
        most_common, count = counts.most_common(1)[0]

        if count >= self.min_count:
            self.stable_gesture = most_common

        return self.stable_gesture

    def reset(self):
        self.history.clear()
        self.stable_gesture = "NONE"