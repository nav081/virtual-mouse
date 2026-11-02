"""Small utilities shared by the application."""

from __future__ import annotations

import time
from collections import deque

import cv2


class FpsCounter:
    """Calculate a stable rolling FPS value."""

    def __init__(self, sample_size: int = 30) -> None:
        self._timestamps: deque[float] = deque(maxlen=sample_size)

    def update(self) -> float:
        self._timestamps.append(time.perf_counter())
        if len(self._timestamps) < 2:
            return 0.0
        elapsed = self._timestamps[-1] - self._timestamps[0]
        return (len(self._timestamps) - 1) / elapsed if elapsed > 0 else 0.0


def put_status(frame, text: str, position: tuple[int, int], color=(255, 255, 255)) -> None:
    """Draw readable status text with a dark outline."""
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 4)
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
