import math

class Geometry:

    @staticmethod
    def distance(point1, point2):
        return math.sqrt((point2.x-point1.x)**2 + (point2.y-point1.y)**2)

    @staticmethod
    def angle(p1, p2, p3):
        v1 = (p1.x-p2.x, p1.y-p2.y)
        v2 = (p3.x-p2.x, p3.y-p2.y)

        dot_product = v1[0] * v2[0] + v1[1] * v2[1]

        magnitude1 = math.hypot(*v1)
        magnitude2 = math.hypot(*v2)

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        cos_angle = dot_product / (magnitude1 * magnitude2)
        cos_angle = max(-1.0, min(1.0, cos_angle))

        return math.degrees(math.acos(cos_angle))

    @staticmethod
    def midpoint(p1, p2):
        return (p1.x + p2.x) / 2, (p1.y + p2.y) / 2

    @staticmethod
    def normalized_distance(p1, p2, reference1, reference2):
        reference_distance = Geometry.distance(reference1, reference2)

        if(reference_distance == 0):
            return 0.0

        return Geometry.distance(p1, p2)/reference_distance