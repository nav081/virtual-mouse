"""Safe, smoothed desktop mouse control."""

from __future__ import annotations

from typing import Optional

import pyautogui


class MouseController:
    """Maps camera coordinates to the primary display and smooths movement."""

    def __init__(self, smoothing_factor: float, frame_reduction: int) -> None:
        width, height = pyautogui.size()
        if width <= 0 or height <= 0:
            raise RuntimeError("The primary display returned an invalid resolution.")
        self.screen_width = int(width)
        self.screen_height = int(height)
        self.smoothing_factor = smoothing_factor
        self.frame_reduction = frame_reduction
        self._position: Optional[tuple[float, float]] = None
        self._last_sent_position: Optional[tuple[int, int]] = None
        pyautogui.PAUSE = 0.01

    def move_from_camera(
        self, x: int, y: int, camera_width: int, camera_height: int
    ) -> tuple[int, int]:
        """Convert camera coordinates into smoothed, bounded screen coordinates."""
        left = min(self.frame_reduction, max(camera_width // 2 - 1, 0))
        right = max(camera_width - self.frame_reduction, left + 1)
        top = min(self.frame_reduction, max(camera_height // 2 - 1, 0))
        bottom = max(camera_height - self.frame_reduction, top + 1)
        target_x = self._map(x, left, right, 0, self.screen_width - 1)
        target_y = self._map(y, top, bottom, 0, self.screen_height - 1)

        if self._position is None:
            self._position = (target_x, target_y)
        else:
            self._position = (
                self._position[0] + (target_x - self._position[0]) * self.smoothing_factor,
                self._position[1] + (target_y - self._position[1]) * self.smoothing_factor,
            )
        position = (round(self._position[0]), round(self._position[1]))
        if position != self._last_sent_position:
            pyautogui.moveTo(*position, duration=0)
            self._last_sent_position = position
        return position

    @staticmethod
    def _map(value: int, source_min: int, source_max: int, target_min: int, target_max: int) -> float:
        ratio = (value - source_min) / max(source_max - source_min, 1)
        ratio = max(0.0, min(1.0, ratio))
        return target_min + ratio * (target_max - target_min)

    def click(self) -> None:
        pyautogui.click()

    def right_click(self) -> None:
        pyautogui.rightClick()

    def scroll(self, amount: int) -> None:
        pyautogui.scroll(amount)

    def mouse_down(self) -> None:
        pyautogui.mouseDown()

    def mouse_up(self) -> None:
        pyautogui.mouseUp()
