from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.vision.hand_tracker import HandState


@dataclass
class ControlState:
    """Stable, game-ready gesture control state."""

    hand_detected: bool = False

    # Current grab state.
    is_grabbing: bool = False

    # Edge events.
    grab_started: bool = False
    release_triggered: bool = False

    # Normalized game position: 0.0 -> 1.0
    aim_x: float = 0.5
    aim_y: float = 0.5

    pinch_distance: Optional[float] = None


class GestureController:
    """
    Converts HandState into a stable ControlState.

    Flow:

        No hand
           ↓
        Hand detected
           ↓
        Pinch starts
           ↓
        grab_started = True
           ↓
        Move while pinching
           ↓
        Release pinch
           ↓
        release_triggered = True
    """

    def __init__(self, smoothing: float = 0.25) -> None:
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

    def update(self, hand_state: HandState) -> ControlState:
        """
        Convert raw HandState into stable game controls.
        """

        # --------------------------------------------------
        # No hand detected
        # --------------------------------------------------
        if not hand_state.detected:
            self.reset()

            return ControlState()

        # --------------------------------------------------
        # Missing landmarks
        # --------------------------------------------------
        if hand_state.index_tip is None:
            self._was_grabbing = False

            return ControlState(
                hand_detected=True,
                pinch_distance=hand_state.pinch_distance,
            )

        # --------------------------------------------------
        # Use index fingertip as cursor position
        # --------------------------------------------------
        raw_x, raw_y = hand_state.index_tip

        # Keep values inside normalized bounds.
        raw_x = max(0.0, min(1.0, raw_x))
        raw_y = max(0.0, min(1.0, raw_y))

        # --------------------------------------------------
        # Smooth movement
        # --------------------------------------------------
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

        # --------------------------------------------------
        # Pinch / grab state
        # --------------------------------------------------
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