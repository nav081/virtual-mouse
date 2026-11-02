"""Entry point for Hand Gesture Mouse Controller."""

from __future__ import annotations

import time
from typing import Optional

import cv2

from config import AppConfig, WINDOW_NAME
from config import CAMERA_FPS
from gesture_detector import GestureState, detect_gesture, pixel_distance
from hand_tracker import HandTracker, TrackedHand
from mouse_controller import MouseController
from utils import FpsCounter, put_status


def gesture_name(state: GestureState, dragging: bool) -> str:
    if dragging:
        return "Dragging"
    if state.right_pinch:
        return "Right Click"
    if state.left_pinch:
        return "Click / Drag"
    if state.open_palm:
        return "Scroll Up"
    if state.closed_fist:
        return "Scroll Down"
    return "Move Cursor"


def draw_overlay(
    frame,
    tracker: HandTracker,
    hand: Optional[TrackedHand],
    state: Optional[GestureState],
    fps: float,
    dragging: bool,
) -> None:
    put_status(frame, f"FPS: {fps:.1f}", (20, 35), (0, 255, 0))
    if hand is None or state is None:
        put_status(frame, "Tracking: No hand", (20, 65), (0, 0, 255))
        put_status(frame, "Gesture: None", (20, 95))
        return
    tracker.draw_landmarks(frame, hand)
    put_status(frame, "Tracking: Active", (20, 65), (0, 255, 0))
    put_status(frame, f"Gesture: {gesture_name(state, dragging)}", (20, 95))
    cv2.circle(frame, hand.points[8], 10, (0, 255, 255), cv2.FILLED)
    if state.left_pinch:
        cv2.line(frame, hand.points[8], hand.points[12], (255, 0, 255), 3)
    if state.right_pinch:
        cv2.line(frame, hand.points[4], hand.points[8], (0, 165, 255), 3)


def run(config: AppConfig) -> None:
    config.validate()
    camera = cv2.VideoCapture(config.camera_index, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera_width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera_height)
    camera.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not camera.isOpened():
        raise RuntimeError("Unable to open the webcam. Check its connection and permissions.")

    tracker = HandTracker()
    mouse = MouseController(config.smoothing_factor, config.frame_reduction)
    fps_counter = FpsCounter()
    last_click = 0.0
    last_right_click = 0.0
    last_scroll = 0.0
    was_right_pinch = False
    pinch_started: Optional[float] = None
    dragging = False
    failed_reads = 0

    try:
        while True:
            success, frame = camera.read()
            if not success or frame is None:
                failed_reads += 1
                if failed_reads >= 30:
                    raise RuntimeError("The webcam stopped returning frames.")
                continue
            failed_reads = 0
            frame = cv2.flip(frame, 1)
            hand = tracker.process(frame)
            state = detect_gesture(
                hand.landmarks,
                config.left_click_threshold,
                config.right_click_threshold,
                frame.shape[1],
                frame.shape[0],
            ) if hand else None
            now = time.monotonic()

            if hand and state:
                mouse.move_from_camera(
                    hand.points[8][0], hand.points[8][1], frame.shape[1], frame.shape[0]
                )
                if state.left_pinch:
                    if pinch_started is None:
                        pinch_started = now
                    elif not dragging and now - pinch_started >= config.drag_hold_seconds:
                        mouse.mouse_down()
                        dragging = True
                elif pinch_started is not None:
                    if dragging:
                        mouse.mouse_up()
                        dragging = False
                    elif now - last_click >= config.click_cooldown:
                        mouse.click()
                        last_click = now
                    pinch_started = None
                else:
                    pinch_started = None

                if (
                    state.right_pinch
                    and not was_right_pinch
                    and now - last_right_click >= config.click_cooldown
                ):
                    mouse.right_click()
                    last_right_click = now
                was_right_pinch = state.right_pinch
                if state.open_palm and now - last_scroll >= config.click_cooldown:
                    mouse.scroll(config.scroll_amount)
                    last_scroll = now
                elif state.closed_fist and now - last_scroll >= config.click_cooldown:
                    mouse.scroll(-config.scroll_amount)
                    last_scroll = now
            elif dragging:
                mouse.mouse_up()
                dragging = False
                pinch_started = None
                was_right_pinch = False
            elif state is None:
                was_right_pinch = False

            draw_overlay(frame, tracker, hand, state, fps_counter.update(), dragging)
            cv2.imshow(WINDOW_NAME, frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        if dragging:
            mouse.mouse_up()
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()


def main() -> None:
    try:
        run(AppConfig())
    except (RuntimeError, ValueError) as error:
        print(f"Application error: {error}")


if __name__ == "__main__":
    main()
