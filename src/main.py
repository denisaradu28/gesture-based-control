import cv2
import time
from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer
from gesture_controller import GestureController
from gesture_stabilizer import GestureStabilizer
from click_detector import ClickDetector


def main():
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("Could not open camera")
        return

    tracker = HandTracker()
    recognizer = GestureRecognizer()
    controller = GestureController()

    stabilizers = {
        "Left": GestureStabilizer(),
        "Right": GestureStabilizer()
    }

    click_detectors = {
        "Left": ClickDetector(),
        "Right": ClickDetector()
    }

    start_time = time.monotonic()
    last_timestamp = -1

    try:
        while True:
            success, frame = camera.read()

            if not success:
                break

            frame = cv2.flip(frame, 1)

            timestamp_ms = int((time.monotonic() - start_time) * 1000)
            timestamp_ms = max(timestamp_ms, last_timestamp + 1)
            last_timestamp = timestamp_ms

            frame, landmarks, handedness = tracker.process_frame(frame, timestamp_ms)

            hands = {}

            for i, hand in enumerate(landmarks):
                if not handedness[i]:
                    continue

                label = handedness[i][0].category_name

                if label not in stabilizers:
                    continue

                gesture, distance = recognizer.recognize(hand)
                stable = stabilizers[label].update(gesture)

                hands[label] = {
                    "landmarks": hand,
                    "gesture": gesture,
                    "stable": stable
                }

            for label in ("Left", "Right"):
                if label not in hands:
                    stabilizers[label].reset()
                    click_detectors[label].update("NONE")

            scroll_mode = (
                "Left" in hands
                and "Right" in hands
                and hands["Right"]["stable"] == "OPEN_PALM"
            )

            scroll_direction = None

            if scroll_mode:
                left_gesture = hands["Left"]["stable"]

                if left_gesture == "POINT":
                    scroll_direction = "DOWN"
                elif left_gesture == "SCROLL":
                    scroll_direction = "UP"

            if scroll_direction:
                controller.scroll(scroll_direction)
                cv2.putText(frame, f"SCROLL {scroll_direction}", (20, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            cursor_moved = False

            if not scroll_mode:
                for label in ("Left", "Right"):
                    if label not in hands:
                        continue

                    hand = hands[label]["landmarks"]

                    if hands[label]["stable"] == "POINT" and not cursor_moved:
                        controller.move_cursor(hand[8])
                        cursor_moved = True

                    if click_detectors[label].update(hands[label]["gesture"]):
                        if label == "Left":
                            controller.left_click()
                            print("LEFT HAND: SINGLE CLICK")
                        elif label == "Right":
                            controller.double_click()
                            print("RIGHT HAND: DOUBLE CLICK")
            else:
                for label in ("Left", "Right"):
                    click_detectors[label].update("NONE")

            if not cursor_moved:
                controller.reset()

            for i, label in enumerate(("Left", "Right")):
                if label in hands:
                    cv2.putText(frame, f"{label}: {hands[label]['stable']}",
                                (20, 130 + i * 40), cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0, 255, 0), 2)

            cv2.imshow("Gesture Based Control", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        tracker.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()