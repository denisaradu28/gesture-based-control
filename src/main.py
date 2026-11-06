import cv2
import time
from hand_tracker import HandTracker

def main():
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("Could not open camera")
        return

    tracker = HandTracker()

    start_time = time.monotonic()
    last_timestamp = -1

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("Could not read camera")
                break

            frame = cv2.flip(frame, 1)

            timestamp_ms = int((time.monotonic() - start_time) * 1000)

            timestamp_ms = max(timestamp_ms, last_timestamp + 1)
            last_timestamp = timestamp_ms

            frame, landmarks = tracker.process_frame(frame, timestamp_ms)

            cv2.putText(frame, f"Hands detected: {len(landmarks)}", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            cv2.imshow("Gesture Based Control", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        camera.release()
        tracker.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()