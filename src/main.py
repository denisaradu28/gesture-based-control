
import cv2
import time
from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer
from gesture_controller import GestureController
from gesture_stabilizer import GestureStabilizer
from click_detector import ClickDetector
from shortcut_detector import ShortcutDetector


def main():
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 30)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not camera.isOpened():
        print("Could not open camera")
        return

    tracker = HandTracker()
    controller = GestureController()

    recognizers = {"Left": GestureRecognizer(), "Right": GestureRecognizer()}
    stabilizers = {"Left": GestureStabilizer(), "Right": GestureStabilizer()}

    click_detector = ClickDetector()
    shortcut_detector = ShortcutDetector()

    active_hand = None
    missing_frames = 0
    start_time = time.monotonic()
    last_timestamp = -1

    try:
        while True:
            success, frame = camera.read()
            if not success: break

            frame = cv2.flip(frame, 1)

            timestamp_ms = int((time.monotonic() - start_time) * 1000)
            timestamp_ms = max(timestamp_ms, last_timestamp + 1)
            last_timestamp = timestamp_ms

            frame, landmarks, handedness = tracker.process_frame(frame, timestamp_ms)

            hands = {}

            for i, hand in enumerate(landmarks):
                if i >= len(handedness) or not handedness[i]: continue

                label = handedness[i][0].category_name
                if label not in recognizers: continue

                hands[label] = hand

            if active_hand not in hands:
                missing_frames += 1

                if active_hand is None or missing_frames >= 5:
                    controller.release_all()
                    click_detector.reset()
                    shortcut_detector.update("NONE")

                    for stabilizer in stabilizers.values():
                        stabilizer.reset()

                    active_hand = next(iter(hands), None)
                    missing_frames = 0
            else:
                missing_frames = 0

            if active_hand in hands:
                hand = hands[active_hand]

                gesture, distance = recognizers[active_hand].recognize(hand)
                stable_gesture = stabilizers[active_hand].update(gesture)

                action = click_detector.update(stable_gesture)

                if action == "SINGLE_CLICK":
                    controller.left_click()
                    print("SINGLE CLICK")

                elif action == "DOUBLE_CLICK":
                    controller.double_click()
                    print("DOUBLE CLICK")

                elif action == "RIGHT_CLICK":
                    controller.right_click()
                    print("RIGHT CLICK")

                elif action == "DRAG_START":
                    controller.drag_start()
                    print("DRAG START")

                elif action == "DRAG_END":
                    controller.drag_end()
                    print("DRAG END")

                shortcut = shortcut_detector.update(stable_gesture)

                if shortcut == "ALT_TAB":
                    controller.switch_window()
                    print("ALT + TAB")
                elif shortcut == "COPY":
                    controller.copy()
                    print("COPY")
                elif shortcut == "PASTE":
                    controller.paste()
                    print("PASTE")

                if click_detector.dragging:
                    controller.move_cursor(hand[9])
                elif stable_gesture == "V_MOVE" and gesture == "V_MOVE":
                    controller.move_cursor(hand[8], hand[12])
                elif stable_gesture == "V_MOVE":
                    pass
                else:
                    controller.reset()

                if stable_gesture == "SCROLL" and not click_detector.dragging:
                    controller.scroll(hand[8])
                else:
                    controller.reset_scroll()

                cv2.putText(frame, f"Hand: {active_hand}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                cv2.putText(frame, f"Gesture: {stable_gesture}", (15, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

                if click_detector.dragging:
                    cv2.putText(frame, "DRAGGING", (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            else:
                controller.release_all()
                shortcut_detector.update("NONE")
                click_detector.reset()

            cv2.imshow("Gesture Based Control", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"): break

    finally:
        controller.release_all()
        camera.release()
        tracker.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()