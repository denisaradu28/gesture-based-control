import cv2
import time
from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer
from gesture_controller import GestureController
from gesture_stabilizer import GestureStabilizer
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
    controller = GestureController(use_kalman=True)
    recognizer = GestureRecognizer()

    stabilizers = {"Left": GestureStabilizer(), "Right": GestureStabilizer()}
    shortcut_detector = ShortcutDetector()

    click_gestures = ("LEFT_CLICK_GESTURE", "RIGHT_CLICK_GESTURE", "DOUBLE_CLICK_GESTURE")
    last_click_gesture = None
    click_start = None
    click_delay = 0.25
    click_triggered = False

    dragging = False
    drag_release_frames = 0
    drag_release_threshold = 3

    try:
        while True:
            success, frame = camera.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            hands = tracker.detect(frame)

            right_hand = hands["Right"]
            left_hand = hands["Left"]

            if right_hand is None and dragging:
                controller.drag_end()
                dragging = False
                drag_release_frames = 0
                print("DRAG END")

            if right_hand is not None:
                gesture, distance = recognizer.recognize(right_hand, "Right")
                stable = stabilizers["Right"].update(gesture)

                if dragging:
                    controller.move_cursor(right_hand[8])
                elif stable == "POINT" and gesture == "POINT":
                    controller.move_cursor(right_hand[8])
                else:
                    controller.reset()

                if stable == "SCROLL" and gesture == "SCROLL" and not dragging:
                    controller.scroll(right_hand[8])
                else:
                    controller.reset_scroll()

                if stable in click_gestures and gesture == stable and not dragging:
                    if last_click_gesture != stable:
                        last_click_gesture = stable
                        click_start = time.monotonic()
                        click_triggered = False

                    elif not click_triggered and click_start is not None:
                        if time.monotonic() - click_start >= click_delay:
                            if stable == "LEFT_CLICK_GESTURE":
                                controller.left_click()
                                print("LEFT CLICK")

                            elif stable == "RIGHT_CLICK_GESTURE":
                                controller.right_click()
                                print("RIGHT CLICK")

                            elif stable == "DOUBLE_CLICK_GESTURE":
                                controller.double_click()
                                print("DOUBLE CLICK")

                            click_triggered = True

                else:
                    last_click_gesture = None
                    click_start = None
                    click_triggered = False

                cv2.putText(frame, f"Right: {stable}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

            else:
                stabilizers["Right"].reset()
                controller.reset()
                controller.reset_scroll()
                last_click_gesture = None
                click_start = None
                click_triggered = False

            if left_hand is not None:
                gesture, distance = recognizer.recognize(left_hand, "Left")
                stable = stabilizers["Left"].update(gesture)

                if not dragging:
                    if stable == "FIST" and gesture == "FIST" and right_hand is not None:
                        controller.drag_start()
                        dragging = True
                        drag_release_frames = 0
                        print("DRAG START")

                else:
                    if gesture != "FIST":
                        drag_release_frames += 1
                    else:
                        drag_release_frames = 0

                    if drag_release_frames >= drag_release_threshold:
                        controller.drag_end()
                        dragging = False
                        drag_release_frames = 0
                        print("DRAG END")

                shortcut = shortcut_detector.update(stable)

                if shortcut == "ALT_TAB":
                    controller.switch_window()
                    print("ALT + TAB")

                elif shortcut == "COPY":
                    controller.copy()
                    print("COPY")

                elif shortcut == "PASTE":
                    controller.paste()
                    print("PASTE")

                cv2.putText(frame, f"Left: {stable}", (15, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

            else:
                stabilizers["Left"].reset()
                shortcut_detector.reset()
                drag_release_frames = 0

                if dragging:
                    controller.drag_end()
                    dragging = False
                    print("DRAG END")

            if dragging:
                cv2.putText(frame, "DRAGGING", (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            cv2.imshow("Gesture Based Control", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        controller.release_all()
        camera.release()
        tracker.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()