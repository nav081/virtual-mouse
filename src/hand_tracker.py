"""MediaPipe hand landmark tracking."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from urllib.request import urlopen

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


@dataclass(frozen=True)
class TrackedHand:
    """A detected hand and its pixel-space landmarks."""

    landmarks: Any
    points: tuple[tuple[int, int], ...]
    handedness: str


class HandTracker:
    """Lightweight one-hand MediaPipe tracker."""

    def __init__(
        self,
        detection_confidence: float = 0.7,
        tracking_confidence: float = 0.7,
    ) -> None:
        model_path = self._ensure_model()
        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self._hands = vision.HandLandmarker.create_from_options(options)
        self._last_timestamp_ms = -1

    @staticmethod
    def _ensure_model() -> Path:
        model_directory = Path.home() / ".cache" / "hand-gesture-mouse"
        model_path = model_directory / "hand_landmarker.task"
        if model_path.exists():
            return model_path
        model_directory.mkdir(parents=True, exist_ok=True)
        model_url = (
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
            "hand_landmarker/float16/1/hand_landmarker.task"
        )
        try:
            with urlopen(model_url, timeout=30) as response:
                model_path.write_bytes(response.read())
        except Exception as error:
            model_path.unlink(missing_ok=True)
            raise RuntimeError(
                "Unable to download the MediaPipe hand model. "
                "Check your internet connection and try again."
            ) from error
        return model_path

    def process(self, frame: np.ndarray) -> Optional[TrackedHand]:
        """Process a BGR frame and return one hand, if present."""
        height, width = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int(cv2.getTickCount() * 1000 / cv2.getTickFrequency())
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms
        result = self._hands.detect_for_video(image, timestamp_ms)
        if not result.hand_landmarks:
            return None

        raw_landmarks = result.hand_landmarks[0]
        points = tuple(
            (
                min(max(int(point.x * width), 0), width - 1),
                min(max(int(point.y * height), 0), height - 1),
            )
            for point in raw_landmarks
        )
        handedness = "Unknown"
        if result.handedness:
            handedness = result.handedness[0][0].category_name
        return TrackedHand(raw_landmarks, points, handedness)

    def draw_landmarks(self, frame: np.ndarray, hand: TrackedHand) -> None:
        """Draw the MediaPipe hand skeleton on a frame."""
        connections = (
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17),
        )
        for start, end in connections:
            cv2.line(frame, hand.points[start], hand.points[end], (0, 255, 0), 2)
        for point in hand.points:
            cv2.circle(frame, point, 3, (0, 0, 255), cv2.FILLED)

    def close(self) -> None:
        self._hands.close()
