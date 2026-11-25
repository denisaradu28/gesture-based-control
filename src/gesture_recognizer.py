from geometry import Geometry


class GestureRecognizer:
    def __init__(self, pinch_threshold=0.45):
        self.pinch_threshold = pinch_threshold

    def is_finger_extended(self, hand, mcp, pip, tip):
        return Geometry.angle(hand[mcp], hand[pip], hand[tip]) > 160

    def is_thumb_extended(self, hand):
        angle = Geometry.angle(hand[2], hand[3], hand[4])
        tip_distance = Geometry.distance(hand[4], hand[5])
        joint_distance = Geometry.distance(hand[3], hand[5])

        return angle > 150 and tip_distance > joint_distance * 1.2

    def recognize(self, hand, hand_label):
        distance = Geometry.normalized_distance(hand[4], hand[8], hand[0], hand[9])

        thumb = self.is_thumb_extended(hand)
        index = self.is_finger_extended(hand, 5, 6, 8)
        middle = self.is_finger_extended(hand, 9, 10, 12)
        ring = self.is_finger_extended(hand, 13, 14, 16)
        pinky = self.is_finger_extended(hand, 17, 18, 20)

        if hand_label == "Right":
            if distance < self.pinch_threshold and middle and ring and pinky:
                return "SCROLL", distance

            
            
            if not thumb and index and middle and ring and pinky:
                return "DOUBLE_CLICK_GESTURE", distance

            if index and middle and ring and not pinky:
                return "RIGHT_CLICK_GESTURE", distance

            if index and middle and not ring and not pinky:
                return "LEFT_CLICK_GESTURE", distance

            if index and not middle and not ring and not pinky:
                return "POINT", distance

        elif hand_label == "Left":
            if not index and not middle and not ring and not pinky:
                return "FIST", distance
            if thumb and index and not middle and not ring and not pinky:
                return "PASTE", distance
            if not index and middle and ring and pinky:
                return "COPY", distance
            if index and middle and ring and not pinky:
                return "THREE_FINGERS", distance
            
            

        return "NONE", distance