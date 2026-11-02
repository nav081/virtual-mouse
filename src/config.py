"""Application configuration for Hand Gesture Mouse Controller."""

from dataclasses import dataclass


CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30
SMOOTHING_FACTOR = 0.35
LEFT_CLICK_THRESHOLD = 25.0
RIGHT_CLICK_THRESHOLD = 35.0
CLICK_COOLDOWN = 0.3
FRAME_REDUCTION = 100
SCROLL_AMOUNT = 100
DRAG_HOLD_SECONDS = 0.6
CAMERA_INDEX = 0
WINDOW_NAME = "Hand Gesture Mouse Controller"


@dataclass(frozen=True)
class AppConfig:
    """Validated runtime configuration."""

    camera_width: int = CAMERA_WIDTH
    camera_height: int = CAMERA_HEIGHT
    smoothing_factor: float = SMOOTHING_FACTOR
    left_click_threshold: float = LEFT_CLICK_THRESHOLD
    right_click_threshold: float = RIGHT_CLICK_THRESHOLD
    click_cooldown: float = CLICK_COOLDOWN
    frame_reduction: int = FRAME_REDUCTION
    scroll_amount: int = SCROLL_AMOUNT
    drag_hold_seconds: float = DRAG_HOLD_SECONDS
    camera_index: int = CAMERA_INDEX

    def validate(self) -> None:
        """Raise a clear error for invalid values before opening the camera."""
        if self.camera_width <= 0 or self.camera_height <= 0:
            raise ValueError("Camera dimensions must be positive.")
        if not 0.0 < self.smoothing_factor <= 1.0:
            raise ValueError("SMOOTHING_FACTOR must be between 0 and 1.")
        if self.frame_reduction < 0:
            raise ValueError("FRAME_REDUCTION cannot be negative.")
        if self.click_cooldown < 0 or self.drag_hold_seconds < 0:
            raise ValueError("Gesture timing values cannot be negative.")
