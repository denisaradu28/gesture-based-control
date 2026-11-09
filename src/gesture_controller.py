
import math
import time
import pyautogui


class GestureController:
    def __init__(self, smoothing=0.25):
        self.screen_width, self.screen_height = pyautogui.size()
        self.smoothing = smoothing
        self.margin = 0.15
        self.prev_x = None
        self.prev_y = None
        self.dragging = False
        self.previous_scroll_y = None
        self.scroll_threshold = 0.02
        self.last_scroll_time = 0.0
        self.scroll_interval = 0.08
        self.deadzone = 3

    def move_cursor(self, index_tip, middle_tip=None):
        x = index_tip.x
        y = index_tip.y

        if middle_tip is not None:
            x = (x + middle_tip.x) / 2
            y = (y + middle_tip.y) / 2

        if not math.isfinite(x) or not math.isfinite(y):
            return

        x = max(0.0, min(1.0, (x - self.margin) / (1 - 2 * self.margin)))
        y = max(0.0, min(1.0, (y - self.margin) / (1 - 2 * self.margin)))

        min_x, min_y = 10, 10
        max_x = max(min_x, self.screen_width - 11)
        max_y = max(min_y, self.screen_height - 11)

        target_x = min_x + x * (max_x - min_x)
        target_y = min_y + y * (max_y - min_y)

        if self.prev_x is None:
            self.prev_x, self.prev_y = pyautogui.position()

        distance = math.hypot(target_x - self.prev_x, target_y - self.prev_y)

        if distance < self.deadzone:
            return

        factor = min(0.75, self.smoothing + distance / 1000)

        smooth_x = self.prev_x + factor * (target_x - self.prev_x)
        smooth_y = self.prev_y + factor * (target_y - self.prev_y)

        smooth_x = max(min_x, min(max_x, smooth_x))
        smooth_y = max(min_y, min(max_y, smooth_y))

        pyautogui.moveTo(int(smooth_x), int(smooth_y))

        self.prev_x = smooth_x
        self.prev_y = smooth_y

    def left_click(self):
        pyautogui.click()

    def double_click(self):
        pyautogui.doubleClick(interval=0.1)

    def right_click(self):
        pyautogui.click(button="right")

    def drag_start(self):
        if not self.dragging:
            pyautogui.mouseDown()
            self.dragging = True

    def drag_end(self):
        if self.dragging:
            pyautogui.mouseUp()
            self.dragging = False

    def scroll(self, index_tip):
        y = index_tip.y

        if self.previous_scroll_y is None:
            self.previous_scroll_y = y
            return

        delta = self.previous_scroll_y - y
        now = time.monotonic()

        if abs(delta) >= self.scroll_threshold and now - self.last_scroll_time >= self.scroll_interval:
            pyautogui.scroll(20 if delta > 0 else -20)
            self.previous_scroll_y = y
            self.last_scroll_time = now

    def reset_scroll(self):
        self.previous_scroll_y = None

    def switch_window(self):
        pyautogui.hotkey("alt", "tab")

    def copy(self):
        pyautogui.hotkey("ctrl", "c")

    def paste(self):
        pyautogui.hotkey("ctrl", "v")

    def reset(self):
        self.prev_x = None
        self.prev_y = None

    def release_all(self):
        self.drag_end()
        self.reset()
        self.reset_scroll()