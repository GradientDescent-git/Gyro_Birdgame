from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import cv2

from app.config.gesture_settings import (
    DEFAULT_CAMERA_INDEX,
    DEFAULT_DEAD_ZONE,
    DEFAULT_SENSITIVITY,
    DEFAULT_SMOOTHING,
)
from app.controls.gesture_controller import (
    ControlState,
    GestureController,
)
from app.vision.hand_tracker import HandState, HandTracker


@dataclass(frozen=True)
class GestureState:
    """State returned from the gesture bridge."""

    detected: bool
    x: int
    y: int
    pinching: bool
    pinch_started: bool
    pinch_released: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detected": self.detected,
            "x": self.x,
            "y": self.y,
            "pinching": self.pinching,
            "pinch_started": self.pinch_started,
            "pinch_released": self.pinch_released,
        }


class GestureBridge:
    """
    Connect webcam hand tracking to the VisionBird game.

    Responsibilities:
    - Capture webcam frames safely with camera-disconnect fallback
    - Track player hand using MediaPipe
    - Convert gestures into relative game control events
    - Compute FPS and inference latency for developer debugging
    - Manage camera and vision resource cleanup
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        camera_index: int = DEFAULT_CAMERA_INDEX,
        smoothing: float = DEFAULT_SMOOTHING,
        sensitivity: float = DEFAULT_SENSITIVITY,
        dead_zone: float = DEFAULT_DEAD_ZONE,
        window_name: str = "VisionBird Gesture Control",
        debug_mode: bool = True,
    ) -> None:
        if screen_width <= 0 or screen_height <= 0:
            raise ValueError("screen_width and screen_height must be positive")
        if sensitivity <= 0:
            raise ValueError("sensitivity must be positive")
        if dead_zone < 0:
            raise ValueError("dead_zone cannot be negative")

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.camera_index = camera_index
        self.window_name = window_name
        self.sensitivity = sensitivity
        self.dead_zone = dead_zone
        self.debug_mode = debug_mode

        self.camera: Optional[cv2.VideoCapture] = None
        self.fallback_mode = False

        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                self.fallback_mode = True
        except Exception:
            self.fallback_mode = True

        self.tracker = HandTracker()
        self.controller = GestureController(smoothing=smoothing)

        self.game_x = screen_width // 2
        self.game_y = screen_height // 2

        self._previous_aim: Optional[tuple[float, float]] = None
        self._closed = False

        # Metrics for Performance Overlay
        self._last_frame_time = time.perf_counter()
        self._fps = 0.0
        self._inference_ms = 0.0

    def update(self) -> Dict[str, Any]:
        """Read webcam frame and return latest gesture state for the game engine."""
        if self._closed or self.fallback_mode or self.camera is None:
            return self._empty_state()

        start_time = time.perf_counter()

        success, frame = self.camera.read()
        if not success or frame is None:
            self._reset_tracking_state()
            return self._empty_state()

        # Mirror camera frame for natural interaction
        frame = cv2.flip(frame, 1)

        t_infer_start = time.perf_counter()
        frame, hand_state = self.tracker.process(frame)
        self._inference_ms = (time.perf_counter() - t_infer_start) * 1000.0

        control_state = self.controller.update(hand_state)
        self._update_game_position(control_state)

        # Performance FPS Calculation
        now = time.perf_counter()
        dt = now - self._last_frame_time
        if dt > 0:
            self._fps = 0.9 * self._fps + 0.1 * (1.0 / dt)
        self._last_frame_time = now

        if self.debug_mode:
            self._draw_debug_overlay(frame, hand_state, control_state)
            cv2.imshow(self.window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                self.close()
                return self._empty_state()

            if self._window_closed():
                self.close()
                return self._empty_state()

        return GestureState(
            detected=control_state.hand_detected,
            x=self.game_x,
            y=self.game_y,
            pinching=control_state.is_grabbing,
            pinch_started=control_state.grab_started,
            pinch_released=control_state.release_triggered,
        ).to_dict()

    def _update_game_position(self, control_state: ControlState) -> None:
        if not control_state.hand_detected:
            self._previous_aim = None
            return

        self.game_x = int(round(control_state.aim_x * self.screen_width))
        self.game_y = int(round(control_state.aim_y * self.screen_height))

        self.game_x = max(0, min(self.screen_width - 1, self.game_x))
        self.game_y = max(0, min(self.screen_height - 1, self.game_y))

    def _reset_tracking_state(self) -> None:
        self.controller.reset()
        self._previous_aim = None

    def _empty_state(self) -> Dict[str, Any]:
        return GestureState(
            detected=False,
            x=self.game_x,
            y=self.game_y,
            pinching=False,
            pinch_started=False,
            pinch_released=False,
        ).to_dict()

    def _window_closed(self) -> bool:
        try:
            return cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1
        except cv2.error:
            return True

    def _draw_debug_overlay(
        self, frame: Any, hand_state: HandState, control_state: ControlState
    ) -> None:
        status = "PINCHING" if control_state.is_grabbing else "OPEN"
        color = (0, 255, 0) if control_state.is_grabbing else (0, 255, 255)

        cv2.putText(
            frame,
            f"FPS: {self._fps:.1f} | Inference: {self._inference_ms:.1f}ms",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            f"Hand: {'YES' if hand_state.detected else 'NO'} | State: {control_state.state.name}",
            (20, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
        )

        p_dist = (
            f"{hand_state.pinch_distance:.3f}"
            if hand_state.pinch_distance is not None
            else "N/A"
        )
        cv2.putText(
            frame,
            f"Gesture: {status} | Pinch dist: {p_dist}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._reset_tracking_state()

        if self.camera is not None:
            self.camera.release()
        if self.tracker is not None:
            self.tracker.close()
        try:
            cv2.destroyWindow(self.window_name)
        except cv2.error:
            pass