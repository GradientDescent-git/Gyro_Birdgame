from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.vision.hand_tracker import HandState


@dataclass
class ControlState:
    """Stable, game-ready gesture control state."""

    hand_detected: bool = False

    is_grabbing: bool = False
    grab_started: bool = False
    release_triggered: bool = False

    aim_x: float = 0.5
    aim_y: float = 0.5

    pinch_distance: Optional[float] = None


class GestureController:
    """
    Converts HandState into responsive game-ready controls.

    A higher smoothing value means the controller follows the
    current hand position more closely.

    smoothing = 1.0
        No smoothing / maximum responsiveness

    smoothing = 0.0
        Maximum lag
    """

    def __init__(
        self,
        smoothing: float = 0.85,
    ) -> None:

        if not 0.0 < smoothing <= 1.0:
            raise ValueError(
                "smoothing must be greater than 0 and less than or equal to 1"
            )

        self.smoothing = smoothing

        self._was_grabbing = False
        self._smoothed_position: Optional[tuple[float, float]] = None

    def reset(self) -> None:
        """Reset controller state safely."""

        self._was_grabbing = False
        self._smoothed_position = None

    def update(
        self,
        hand_state: HandState,
    ) -> ControlState:
        """Convert raw HandState into responsive game controls."""

        if not hand_state.detected:
            self.reset()

            return ControlState()

        if hand_state.index_tip is None:
            self._was_grabbing = False

            return ControlState(
                hand_detected=True,
                pinch_distance=hand_state.pinch_distance,
            )

        raw_x, raw_y = hand_state.index_tip

        raw_x = max(0.0, min(1.0, raw_x))
        raw_y = max(0.0, min(1.0, raw_y))

        if self._smoothed_position is None:

            smoothed_x = raw_x
            smoothed_y = raw_y

        else:

            previous_x, previous_y = self._smoothed_position

            alpha = self.smoothing

            smoothed_x = (
                alpha * raw_x
                + (1.0 - alpha) * previous_x
            )

            smoothed_y = (
                alpha * raw_y
                + (1.0 - alpha) * previous_y
            )

        self._smoothed_position = (
            smoothed_x,
            smoothed_y,
        )

        is_grabbing = hand_state.is_pinching

        grab_started = (
            is_grabbing
            and not self._was_grabbing
        )

        release_triggered = (
            self._was_grabbing
            and not is_grabbing
        )

        self._was_grabbing = is_grabbing

        return ControlState(
            hand_detected=True,
            is_grabbing=is_grabbing,
            grab_started=grab_started,
            release_triggered=release_triggered,
            aim_x=smoothed_x,
            aim_y=smoothed_y,
            pinch_distance=hand_state.pinch_distance,
        )