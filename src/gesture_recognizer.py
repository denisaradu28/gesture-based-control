from geometry import Geometry


class GestureRecognizer:
    def __init__(self, pinch_threshold=0.45):
        self.pinch_threshold = pinch_threshold

    def is_finger_extended(self, hand, mcp, pip, tip):
        return Geometry.angle(hand[mcp], hand[pip], hand[tip]) > 160

    def recognize(self, hand):
        distance = Geometry.normalized_distance(hand[4], hand[8], hand[0], hand[9])

        index = self.is_finger_extended(hand, 5, 6, 8)
        middle = self.is_finger_extended(hand, 9, 10, 12)
        ring = self.is_finger_extended(hand, 13, 14, 16)
        pinky = self.is_finger_extended(hand, 17, 18, 20)

        extended_count = sum([index, middle, ring, pinky])

        if index and middle and ring and not pinky:
            return "THREE_FINGERS", distance

        if distance < self.pinch_threshold and middle and ring and pinky:
            return "SCROLL", distance

        if index and middle and not ring and not pinky:
            tip_distance = Geometry.distance(hand[8], hand[12])
            base_distance = Geometry.distance(hand[5], hand[9])
            ratio = tip_distance / max(base_distance, 0.0001)

            if ratio > 1.7:
                return "V_MOVE", ratio

            return "V_CLOSED", ratio

        if not index and middle and ring and pinky:
            return "COPY", distance

        if index and not middle and ring and pinky:
            return "PASTE", distance

        if not index and not middle and ring and pinky:
            return "LEFT_CLICK_GESTURE", distance

        if index and not middle and not ring and not pinky:
            return "RIGHT_CLICK_GESTURE", distance

        if extended_count == 0:
            return "FIST", distance

        if extended_count == 4:
            return "OPEN_PALM", distance

        return "NONE", distance