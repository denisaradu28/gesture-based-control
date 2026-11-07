import pyautogui
import math
import time


class GestureController:
    def __init__(self, smoothing=0.15):
        self.screen_width, self.screen_height = pyautogui.size()
        self.smoothing = smoothing
        self.prev_x = None
        self.prev_y = None
        self.margin = 0.15
        self.last_scroll_time = 0.0
        self.scroll_interval = 0.05

    def move_cursor(self, index_tip):
        x = index_tip.x
        y = index_tip.y

        if not math.isfinite(x) or not math.isfinite(y):
            return

        x = (x - self.margin) / (1 - 2 * self.margin)
        y = (y - self.margin) / (1 - 2 * self.margin)

        x = max(0.0, min(1.0, x))
        y = max(0.0, min(1.0, y))

        safe_margin = 10

        min_x = safe_margin
        max_x = max(min_x, self.screen_width - safe_margin - 1)
        min_y = safe_margin
        max_y = max(min_y, self.screen_height - safe_margin - 1)

        target_x = min_x + x * (max_x - min_x)
        target_y = min_y + y * (max_y - min_y)

        if self.prev_x is None:
            self.prev_x = target_x
            self.prev_y = target_y

        smooth_x = self.prev_x + self.smoothing * (target_x - self.prev_x)
        smooth_y = self.prev_y + self.smoothing * (target_y - self.prev_y)

        smooth_x = max(min_x, min(max_x, smooth_x))
        smooth_y = max(min_y, min(max_y, smooth_y))

        current_x, current_y = pyautogui.position()

        if current_x <= 0 or current_y <= 0:
            self.reset()
            return

        if current_x >= self.screen_width - 1 or current_y >= self.screen_height - 1:
            self.reset()
            return

        pyautogui.moveTo(int(smooth_x), int(smooth_y))

        self.prev_x = smooth_x
        self.prev_y = smooth_y

    def left_click(self):
        pyautogui.click()

    def double_click(self):
        pyautogui.doubleClick(interval=0.1)

    def scroll(self, direction):
        if direction not in ("UP", "DOWN"):
            return

        now = time.monotonic()

        if now - self.last_scroll_time < self.scroll_interval:
            return

        pyautogui.scroll(15 if direction == "UP" else -15)
        self.last_scroll_time = now

    def reset(self):
        self.prev_x = None
        self.prev_y = None