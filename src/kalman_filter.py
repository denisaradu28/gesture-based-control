import cv2
import time
import numpy as np

class KalmanCursorFilter:
    def __init__(self):
        self.kalman = cv2.KalmanFilter(4, 2)

        self.kalman.measurementMatrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=np.float32)

        self.kalman.transitionMatrix = np.eye(4, dtype=np.float32)
        self.kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.002
        self.kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.0002
        self.kalman.errorCovPost = np.eye(4, dtype=np.float32) * 0.1

        self.initialized = False
        self.last_time = None

    def update(self, x, y):
        now = time.monotonic()

        if not self.initialized:
            self.kalman.statePost = np.array([[x], [y], [0], [0]], dtype=np.float32)
            self.initialized = True
            self.last_time = now
            return x, y

        dt = max(0.001, min(now-self.last_time, 0.1))

        self.last_time = now

        self.kalman.transitionMatrix = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        self.kalman.predict()

        measurement = np.array([[x], [y]], dtype=np.float32)
        estimated = self.kalman.correct(measurement)

        return float(estimated[0, 0]), float(estimated[1, 0])

    def reset(self):
        self.initialized = False
        self.last_time = None
