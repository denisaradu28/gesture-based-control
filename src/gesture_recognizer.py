from geometry import Geometry


class GestureRecognizer:
    def __init__(self, pinch_threshold=0.55):
        self.pinch_threshold = pinch_threshold

    def is_finger_extended(self, hand, mcp, pip, tip):
        angle = Geometry.angle(hand[mcp], hand[pip], hand[tip])
        return angle > 160

    def recognize(self, hand):
        distance = Geometry.normalized_distance(hand[4], hand[8], hand[0], hand[9])

        index_extended = self.is_finger_extended(hand, 5, 6, 8)
        middle_extended = self.is_finger_extended(hand, 9, 10, 12)
        ring_extended = self.is_finger_extended(hand, 13, 14, 16)
        pinky_extended = self.is_finger_extended(hand, 17, 18, 20)

        extended_count = sum([index_extended, middle_extended, ring_extended, pinky_extended])

        if index_extended and middle_extended and not ring_extended and not pinky_extended:
            return "SCROLL", distance

        if distance < self.pinch_threshold:
            return "PINCH", distance

        if extended_count == 4:
            return "OPEN_PALM", distance

        if extended_count == 0:
            return "FIST", distance

        if index_extended and not middle_extended and not ring_extended and not pinky_extended:
            return "POINT", distance

        return "NONE", distance