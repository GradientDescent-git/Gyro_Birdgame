from __future__ import annotations

import cv2

from app.vision.hand_tracker import HandTracker


class GestureBridge:
    """
    VisionBird gesture input bridge.

    Responsibilities:
    - Read webcam frames.
    - Detect one hand.
    - Map the index finger to game coordinates.
    - Detect pinch start and pinch release.

    Slingshot pull mechanics are intentionally NOT handled here.
    The game controls and physics remain inside main.py.
    """

    def __init__(
        self,
        screen_width: int = 1200,
        screen_height: int = 650,
        camera_index: int = 0,
    ) -> None:

        self.screen_width = screen_width
        self.screen_height = screen_height

        # ----------------------------------------------------
        # CAMERA
        # ----------------------------------------------------

        self.camera = cv2.VideoCapture(camera_index)

        if not self.camera.isOpened():
            raise RuntimeError("Could not open webcam.")

        self.camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            640,
        )

        self.camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            480,
        )

        # ----------------------------------------------------
        # HAND TRACKER
        # ----------------------------------------------------

        self.tracker = HandTracker()

        # ----------------------------------------------------
        # PINCH STATE
        # ----------------------------------------------------

        self.previous_pinching = False

        # ----------------------------------------------------
        # GAME CURSOR
        # ----------------------------------------------------

        self.game_x = screen_width // 2
        self.game_y = screen_height // 2

        self.smooth_x = float(self.game_x)
        self.smooth_y = float(self.game_y)

        # Cursor smoothing only.
        self.smoothing = 0.30

        # ----------------------------------------------------
        # CAMERA WINDOW
        # ----------------------------------------------------

        self.window_name = "VisionBird Hand Control"

        cv2.namedWindow(
            self.window_name,
            cv2.WINDOW_NORMAL,
        )

        cv2.resizeWindow(
            self.window_name,
            640,
            480,
        )

        print()
        print("GestureBridge initialized successfully.")
        print("Hand tracking ready.")
        print()

    def clamp(
        self,
        value: int,
        minimum: int,
        maximum: int,
    ) -> int:

        return max(
            minimum,
            min(
                maximum,
                value,
            ),
        )

    def update(self) -> dict:

        # ----------------------------------------------------
        # READ CAMERA
        # ----------------------------------------------------

        success, frame = self.camera.read()

        if not success:

            pinch_released = self.previous_pinching

            self.previous_pinching = False

            return {
                "detected": False,
                "x": self.game_x,
                "y": self.game_y,
                "pinching": False,
                "pinch_started": False,
                "pinch_released": pinch_released,
            }

        # ----------------------------------------------------
        # MIRROR CAMERA
        # ----------------------------------------------------

        frame = cv2.flip(
            frame,
            1,
        )

        # ----------------------------------------------------
        # DETECT HAND
        # ----------------------------------------------------

        frame, hand_state = self.tracker.process(
            frame
        )

        # ----------------------------------------------------
        # PINCH EVENTS
        # ----------------------------------------------------

        current_pinching = (
            hand_state.detected
            and hand_state.is_pinching
        )

        pinch_started = (
            current_pinching
            and not self.previous_pinching
        )

        pinch_released = (
            not current_pinching
            and self.previous_pinching
        )

        # ----------------------------------------------------
        # MAP INDEX FINGER TO GAME
        # ----------------------------------------------------

        if (
            hand_state.detected
            and hand_state.index_tip is not None
        ):

            index_x, index_y = hand_state.index_tip

            target_x = int(
                index_x * self.screen_width
            )

            target_y = int(
                index_y * self.screen_height
            )

            # Smooth cursor movement.

            self.smooth_x += (
                target_x - self.smooth_x
            ) * self.smoothing

            self.smooth_y += (
                target_y - self.smooth_y
            ) * self.smoothing

            self.game_x = self.clamp(
                int(self.smooth_x),
                0,
                self.screen_width - 1,
            )

            self.game_y = self.clamp(
                int(self.smooth_y),
                0,
                self.screen_height - 1,
            )

        # ----------------------------------------------------
        # CAMERA UI
        # ----------------------------------------------------

        if hand_state.detected:

            hand_text = "HAND DETECTED"

        else:

            hand_text = "NO HAND"

        if current_pinching:

            gesture_text = "PINCHING"

        else:

            gesture_text = "OPEN HAND"

        cv2.putText(
            frame,
            hand_text,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        cv2.putText(
            frame,
            gesture_text,
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        if hand_state.pinch_distance is not None:

            distance_text = (
                f"Pinch: "
                f"{hand_state.pinch_distance:.3f}"
            )

            cv2.putText(
                frame,
                distance_text,
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

        cursor_text = (
            f"Game Cursor: "
            f"({self.game_x}, {self.game_y})"
        )

        cv2.putText(
            frame,
            cursor_text,
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
            "Move hand while pinching = pull",
            (20, 460),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        # ----------------------------------------------------
        # DISPLAY CAMERA
        # ----------------------------------------------------

        cv2.imshow(
            self.window_name,
            frame,
        )

        key = cv2.waitKey(1) & 0xFF

        if key == 27:

            # ESC should not accidentally launch a bird.
            current_pinching = False
            pinch_started = False
            pinch_released = False

        # ----------------------------------------------------
        # SAVE STATE
        # ----------------------------------------------------

        self.previous_pinching = current_pinching

        # ----------------------------------------------------
        # RETURN GAME INPUT
        # ----------------------------------------------------

        return {
            "detected": hand_state.detected,
            "x": self.game_x,
            "y": self.game_y,
            "pinching": current_pinching,
            "pinch_started": pinch_started,
            "pinch_released": pinch_released,
        }

    def close(self) -> None:

        print("Closing VisionBird GestureBridge...")

        if self.camera is not None:
            self.camera.release()

        if self.tracker is not None:
            self.tracker.close()

        cv2.destroyAllWindows()

        print("GestureBridge closed.")