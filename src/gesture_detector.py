"""Reusable finger and gesture detection helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class GestureState:
    """The gesture facts used by the application action layer."""

    fingers: Mapping[str, bool]
    index_middle_distance: float
    thumb_index_distance: float
    left_pinch: bool
    right_pinch: bool
    open_palm: bool
    closed_fist: bool


def _point(landmarks: Any, index: int) -> tuple[float, float]:
    point = landmarks.landmark[index] if hasattr(landmarks, "landmark") else landmarks[index]
    return float(point.x), float(point.y)


def _distance(first: tuple[float, float], second: tuple[float, float]) -> float:
    return hypot(first[0] - second[0], first[1] - second[1])


def _pixel_distance(
    first: tuple[float, float],
    second: tuple[float, float],
    image_width: int,
    image_height: int,
) -> float:
    return hypot(
        (first[0] - second[0]) * image_width,
        (first[1] - second[1]) * image_height,
    )


def fingers_up(hand_landmarks: Any) -> dict[str, bool]:
    """Return whether each finger is extended using normalized landmarks."""
    wrist = _point(hand_landmarks, 0)
    fingertip_indices = {"index": 8, "middle": 12, "ring": 16, "pinky": 20}
    pip_indices = {"index": 6, "middle": 10, "ring": 14, "pinky": 18}
    result = {
        finger: _distance(_point(hand_landmarks, tip), wrist)
        > _distance(_point(hand_landmarks, pip), wrist)
        for finger, tip in fingertip_indices.items()
        for pip in [pip_indices[finger]]
    }

    thumb_tip = _point(hand_landmarks, 4)
    thumb_ip = _point(hand_landmarks, 3)
    result["thumb"] = _distance(thumb_tip, wrist) > _distance(thumb_ip, wrist)
    return {
        finger: result[finger]
        for finger in ("thumb", "index", "middle", "ring", "pinky")
    }


def detect_gesture(
    hand_landmarks: Any,
    index_middle_threshold: float,
    thumb_index_threshold: float,
    image_width: int,
    image_height: int,
) -> GestureState:
    """Calculate gesture facts from a MediaPipe landmark collection."""
    fingers = fingers_up(hand_landmarks)
    index_middle_distance = (
        _pixel_distance(
            _point(hand_landmarks, 8),
            _point(hand_landmarks, 12),
            image_width,
            image_height,
        )
    )
    thumb_index_distance = (
        _pixel_distance(
            _point(hand_landmarks, 4),
            _point(hand_landmarks, 8),
            image_width,
            image_height,
        )
    )
    open_palm = all(fingers.values())
    closed_fist = not any(fingers.values())
    left_pinch = (
        fingers["index"]
        and fingers["middle"]
        and index_middle_distance < index_middle_threshold
    )
    right_pinch = (
        fingers["index"]
        and fingers["thumb"]
        and thumb_index_distance < thumb_index_threshold
    )
    return GestureState(
        fingers=fingers,
        index_middle_distance=index_middle_distance,
        thumb_index_distance=thumb_index_distance,
        left_pinch=left_pinch,
        right_pinch=right_pinch,
        open_palm=open_palm,
        closed_fist=closed_fist,
    )


def pixel_distance(points: Sequence[tuple[int, int]], first: int, second: int) -> float:
    """Measure distance between two pixel-space landmarks."""
    return _distance(points[first], points[second])
