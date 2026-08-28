from __future__ import annotations

import cv2

from app.controls.gesture_controller import (
    ControlState,
    GestureController,
)
from app.vision.hand_tracker import HandTracker


class GestureBridge:
    """
    Connects the webcam + hand tracking pipeline to VisionBird.

    The game receives a simple dictionary:

        detected
        x
        y
        pinching
        pinch_started
        pinch_released
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        camera_index: int = 0,
        smoothing: float = 0.25,
        window_name: str = "VisionBird Gesture Control",
    ) -> None:

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.camera_index = camera_index
        self.window_name = window_name

        self.camera = cv2.VideoCapture(camera_index)

        if not self.camera.isOpened():
            self.camera.release()

            raise RuntimeError(
                f"Could not open camera index {camera_index}"
            )

        self.tracker = HandTracker()

        self.controller = GestureController(
            smoothing=smoothing
        )

        self.game_x = screen_width // 2
        self.game_y = screen_height // 2

        self._closed = False

    def update(self) -> dict[str, object]:
        """
        Capture one frame and return game-ready gesture state.
        """

        if self._closed:
            return self._empty_state()

        success, frame = self.camera.read()

        if not success or frame is None:
            return self._empty_state()

        # Mirror once here.
        frame = cv2.flip(frame, 1)

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

        # ESC only closes gesture control safely.
        if key == 27:
            self.controller.reset()

            return {
                "detected": False,
                "x": self.game_x,
                "y": self.game_y,
                "pinching": False,
                "pinch_started": False,
                "pinch_released": False,
            }

        return {
            "detected": control_state.hand_detected,
            "x": self.game_x,
            "y": self.game_y,
            "pinching": control_state.is_grabbing,
            "pinch_started": control_state.grab_started,
            "pinch_released": control_state.release_triggered,
        }

    def _update_game_position(
        self,
        control_state: ControlState,
    ) -> None:
        """Convert normalized position to game coordinates."""

        if not control_state.hand_detected:
            return

        x = int(
            control_state.aim_x
            * (self.screen_width - 1)
        )

        y = int(
            control_state.aim_y
            * (self.screen_height - 1)
        )

        self.game_x = max(
            0,
            min(
                self.screen_width - 1,
                x,
            ),
        )

        self.game_y = max(
            0,
            min(
                self.screen_height - 1,
                y,
            ),
        )

    def _empty_state(self) -> dict[str, object]:
        return {
            "detected": False,
            "x": self.game_x,
            "y": self.game_y,
            "pinching": False,
            "pinch_started": False,
            "pinch_released": False,
        }

    def _draw_debug_overlay(
        self,
        frame,
        hand_state,
        control_state: ControlState,
    ) -> None:

        status = (
            "PINCHING"
            if control_state.is_grabbing
            else "OPEN"
        )

        color = (
            (0, 255, 0)
            if control_state.is_grabbing
            else (0, 165, 255)
        )

        cv2.putText(
            frame,
            f"Hand: {'Detected' if hand_state.detected else 'Not detected'}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

        cv2.putText(
            frame,
            f"Gesture: {status}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

        if hand_state.pinch_distance is not None:

            cv2.putText(
                frame,
                (
                    "Pinch distance: "
                    f"{hand_state.pinch_distance:.3f}"
                ),
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

        cv2.putText(
            frame,
            (
                "Game cursor: "
                f"({self.game_x}, {self.game_y})"
            ),
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            "Move index finger to aim",
            (20, 390),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            "Pinch thumb + index = grab",
            (20, 425),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            "Release pinch = launch",
            (20, 460),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

    def close(self) -> None:
        """Release all camera and vision resources safely."""

        if self._closed:
            return

        self._closed = True

        self.controller.reset()

        if self.camera is not None:
            self.camera.release()

        if self.tracker is not None:
            self.tracker.close()

        cv2.destroyAllWindows()