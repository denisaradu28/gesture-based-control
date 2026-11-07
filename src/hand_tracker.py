import cv2
import mediapipe as mp
from pathlib import Path

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandTracker():
    def __init__(self, num_hands=2):
        model_path = (
            Path(__file__).resolve().parent.parent
            / "models"
            / "hand_landmarker.task"
        )

        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(
                model_asset_path=str(model_path)
            ),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=num_hands,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.landmarker = vision.HandLandmarker.create_from_options(
            options
        )

        self.connections = mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS

    def process_frame(self, frame, timestamp_ms):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        height, width, _ = frame.shape

        for hand_landmarks in result.hand_landmarks:
            points = []

            for landmark in hand_landmarks:
                x = int(landmark.x * width)
                y = int(landmark.y * height)

                points.append((x, y))

                cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

            for connection in self.connections:
                start = points[connection.start]
                end = points[connection.end]

                cv2.line(frame, start, end, (255, 255, 255), 2)

        return frame, result.hand_landmarks, result.handedness

    def close(self):
        self.landmarker.close()