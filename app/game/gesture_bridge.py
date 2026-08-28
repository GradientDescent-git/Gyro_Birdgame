from __future__ import annotations

from dataclasses import dataclass

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
from app.vision.hand_tracker import HandTracker


@dataclass(frozen=True)
class GestureState:
    """State returned from the gesture bridge."""

    detected: bool
    x: int
    y: int
    pinching: bool
    pinch_started: bool
    pinch_released: bool

    def to_dict(self) -> dict[str, object]:
        """Convert state to the game-compatible format."""

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

    - Capture webcam frames
    - Track the player's hand
    - Convert gestures into game control events
    - Convert normalized hand movement into relative
      in-game cursor movement
    - Apply sensitivity and dead-zone filtering
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
    ) -> None:

        if screen_width <= 0:
            raise ValueError(
                "screen_width must be greater than 0"
            )

        if screen_height <= 0:
            raise ValueError(
                "screen_height must be greater than 0"
            )

        if sensitivity <= 0:
            raise ValueError(
                "sensitivity must be greater than 0"
            )

        if dead_zone < 0:
            raise ValueError(
                "dead_zone cannot be negative"
            )

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.camera_index = camera_index
        self.window_name = window_name

        self.sensitivity = sensitivity
        self.dead_zone = dead_zone

        self.camera = cv2.VideoCapture(
            camera_index
        )

        if not self.camera.isOpened():

            self.camera.release()

            raise RuntimeError(
                f"Could not open camera index "
                f"{camera_index}"
            )

        self.tracker = HandTracker()

        self.controller = GestureController(
            smoothing=smoothing
        )

        # Start at the center of the game window.
        self.game_x = screen_width // 2
        self.game_y = screen_height // 2

        # Previous normalized hand position used for
        # relative movement.
        self._previous_aim: tuple[float, float] | None = None

        self._closed = False

    def update(self) -> dict[str, object]:
        """
        Read one webcam frame and return the latest
        gesture state for the game.
        """

        if self._closed:
            return self._empty_state()

        success, frame = self.camera.read()

        if not success or frame is None:

            self._reset_tracking_state()

            return self._empty_state()

        # Mirror once so movement feels natural.
        frame = cv2.flip(
            frame,
            1,
        )

        frame, hand_state = self.tracker.process(
            frame
        )

        control_state = self.controller.update(
            hand_state
        )

        self._update_game_position(
            control_state
        )

        self._draw_debug_overlay(
            frame,
            hand_state,
            control_state,
        )

        cv2.imshow(
            self.window_name,
            frame,
        )

        key = cv2.waitKey(1) & 0xFF

        # ESC disables gesture control cleanly.
        if key == 27:

            self.close()

            return self._empty_state()

        # Handle manual closing of the debug window.
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

    def _update_game_position(
        self,
        control_state: ControlState,
    ) -> None:
        """
        Convert normalized hand movement into relative
        in-game cursor movement.
        """

        if not control_state.hand_detected:

            self._previous_aim = None

            return

        current_x = control_state.aim_x
        current_y = control_state.aim_y

        # First frame establishes a reference position and
        # prevents an initial cursor jump.
        if self._previous_aim is None:

            self._previous_aim = (
                current_x,
                current_y,
            )

            return

        previous_x, previous_y = self._previous_aim

        delta_x = current_x - previous_x
        delta_y = current_y - previous_y

        self._previous_aim = (
            current_x,
            current_y,
        )

        # Ignore tiny tracking jitter.
        if abs(delta_x) < self.dead_zone:
            delta_x = 0.0

        if abs(delta_y) < self.dead_zone:
            delta_y = 0.0

        movement_x = (
            delta_x
            * self.screen_width
            * self.sensitivity
        )

        movement_y = (
            delta_y
            * self.screen_height
            * self.sensitivity
        )

        self.game_x += int(
            round(movement_x)
        )

        self.game_y += int(
            round(movement_y)
        )

        self._clamp_game_position()

    def _clamp_game_position(
        self,
    ) -> None:
        """Keep the gesture cursor inside the game window."""

        self.game_x = max(
            0,
            min(
                self.screen_width - 1,
                self.game_x,
            ),
        )

        self.game_y = max(
            0,
            min(
                self.screen_height - 1,
                self.game_y,
            ),
        )

    def _reset_tracking_state(
        self,
    ) -> None:
        """Reset transient gesture tracking state."""

        self.controller.reset()

        self._previous_aim = None

    def _empty_state(
        self,
    ) -> dict[str, object]:
        """Return a neutral game control state."""

        return GestureState(
            detected=False,
            x=self.game_x,
            y=self.game_y,
            pinching=False,
            pinch_started=False,
            pinch_released=False,
        ).to_dict()

    def _window_closed(
        self,
    ) -> bool:
        """Return True when the OpenCV debug window is closed."""

        try:

            return (
                cv2.getWindowProperty(
                    self.window_name,
                    cv2.WND_PROP_VISIBLE,
                )
                < 1
            )

        except cv2.error:

            return True

    def _draw_debug_overlay(
        self,
        frame,
        hand_state,
        control_state: ControlState,
    ) -> None:
        """Draw live debugging information."""

        if control_state.is_grabbing:

            status = "PINCHING"
            color = (
                0,
                255,
                0,
            )

        elif control_state.release_triggered:

            status = "RELEASED"
            color = (
                0,
                165,
                255,
            )

        else:

            status = "OPEN"
            color = (
                255,
                255,
                0,
            )

        hand_label = (
            "Hand: Detected"
            if hand_state.detected
            else "Hand: Not detected"
        )

        cv2.putText(
            frame,
            hand_label,
            (
                20,
                40,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

        cv2.putText(
            frame,
            f"Gesture: {status}",
            (
                20,
                80,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

        if (
            hand_state.detected
            and hand_state.pinch_distance is not None
        ):

            cv2.putText(
                frame,
                (
                    "Pinch distance: "
                    f"{hand_state.pinch_distance:.3f}"
                ),
                (
                    20,
                    120,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (
                    255,
                    255,
                    255,
                ),
                2,
            )

        cv2.putText(
            frame,
            (
                "Game cursor: "
                f"({self.game_x}, {self.game_y})"
            ),
            (
                20,
                160,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (
                255,
                255,
                255,
            ),
            2,
        )

        cv2.putText(
            frame,
            (
                "Sensitivity: "
                f"{self.sensitivity:.2f}x"
            ),
            (
                20,
                200,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (
                255,
                255,
                255,
            ),
            2,
        )

        cv2.putText(
            frame,
            (
                "Dead zone: "
                f"{self.dead_zone:.4f}"
            ),
            (
                20,
                235,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (
                255,
                255,
                255,
            ),
            2,
        )

        cv2.putText(
            frame,
            "Move index finger to aim",
            (
                20,
                390,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (
                255,
                255,
                255,
            ),
            2,
        )

        cv2.putText(
            frame,
            "Pinch thumb + index = grab",
            (
                20,
                425,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (
                255,
                255,
                255,
            ),
            2,
        )

        cv2.putText(
            frame,
            "Release pinch = launch",
            (
                20,
                460,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (
                255,
                255,
                255,
            ),
            2,
        )

        cv2.putText(
            frame,
            "ESC = disable gesture control",
            (
                20,
                495,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (
                255,
                255,
                255,
            ),
            2,
        )

    def close(
        self,
    ) -> None:
        """
        Release camera and vision resources safely.

        Safe to call multiple times.
        """

        if self._closed:
            return

        self._closed = True

        self._reset_tracking_state()

        if self.camera is not None:

            self.camera.release()

        if self.tracker is not None:

            self.tracker.close()

        try:

            cv2.destroyWindow(
                self.window_name
            )

        except cv2.error:

            pass