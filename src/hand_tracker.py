import cv2
import time
import mediapipe as mp
from pathlib import Path
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandTracker:
    def __init__(self):
        model_path = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"

        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.detector = vision.HandLandmarker.create_from_options(options)
        self.connections = mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS

        self.start_time = time.monotonic()
        self.last_timestamp = -1

    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        timestamp = int((time.monotonic() - self.start_time) * 1000)
        timestamp = max(timestamp, self.last_timestamp + 1)
        self.last_timestamp = timestamp

        result = self.detector.detect_for_video(mp_image, timestamp)

        hands = {"Left": None, "Right": None}
        height, width, _ = frame.shape

        for i, landmarks in enumerate(result.hand_landmarks):
            if i >= len(result.handedness) or not result.handedness[i]: continue

            hand_label = result.handedness[i][0].category_name
            hand_label = "Left" if hand_label == "Right" else "Right"

            if hand_label not in hands: continue        

            hands[hand_label] = landmarks
            points = []

            for landmark in landmarks:
                x = int(landmark.x * width)
                y = int(landmark.y * height)

                points.append((x, y))
                cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

            for connection in self.connections:
                start = points[connection.start]
                end = points[connection.end]
                cv2.line(frame, start, end, (255, 255, 255), 2)

            cv2.putText(frame, hand_label, points[0], cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        return hands

    def close(self):
        self.detector.close()