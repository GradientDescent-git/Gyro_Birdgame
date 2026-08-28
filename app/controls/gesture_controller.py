from dataclasses import dataclass
from typing import Optional, Tuple

from app.vision.hand_tracker import HandState


@dataclass
class ControlState:
    """Stable game-ready control state."""

    hand_detected: bool = False
    is_grabbing: bool = False
    release_triggered: bool = False

    # Normalized position: 0.0 -> 1.0
    aim_x: float = 0.5
    aim_y: float = 0.5

    pinch_distance: Optional[float] = None


class GestureController:
    """
    Converts HandState into stable game controls.

    Flow:

        Hand visible
            ↓
        Pinch
            ↓
        Move hand while pinching
            ↓
        Release pinch
            ↓
        release_triggered = True
    """

    def __init__(
        self,
        smoothing: float = 0.25,
    ) -> None:

        self.smoothing = smoothing

        self._was_grabbing = False

        self._smoothed_position: Optional[
            Tuple[float, float]
        ] = None

    def update(
        self,
        hand_state: HandState,
    ) -> ControlState:

        # ------------------------------------------
        # No hand detected
        # ------------------------------------------

        if not hand_state.detected:

            self._was_grabbing = False
            self._smoothed_position = None

            return ControlState()

        # ------------------------------------------
        # Calculate control position
        #
        # Midpoint between thumb and index finger
        # ------------------------------------------

        if (
            hand_state.index_tip is None
            or hand_state.thumb_tip is None
        ):

            return ControlState(
                hand_detected=True,
                is_grabbing=False,
                pinch_distance=hand_state.pinch_distance,
            )

        index_x, index_y = hand_state.index_tip
        thumb_x, thumb_y = hand_state.thumb_tip

        raw_x = (index_x + thumb_x) / 2
        raw_y = (index_y + thumb_y) / 2

        # ------------------------------------------
        # Smooth movement
        # ------------------------------------------

        if self._smoothed_position is None:

            smoothed_x = raw_x
            smoothed_y = raw_y

        else:

            previous_x, previous_y = (
                self._smoothed_position
            )

            alpha = self.smoothing

            smoothed_x = (
                alpha * raw_x
                + (1 - alpha) * previous_x
            )

            smoothed_y = (
                alpha * raw_y
                + (1 - alpha) * previous_y
            )

        self._smoothed_position = (
            smoothed_x,
            smoothed_y,
        )

        # ------------------------------------------
        # Grab state
        # ------------------------------------------

        is_grabbing = hand_state.is_pinching

        # ------------------------------------------
        # Release detection
        #
        # Previous frame = PINCH
        # Current frame  = OPEN
        # ------------------------------------------

        release_triggered = (
            self._was_grabbing
            and not is_grabbing
        )

        self._was_grabbing = is_grabbing

        return ControlState(
            hand_detected=True,
            is_grabbing=is_grabbing,
            release_triggered=release_triggered,
            aim_x=smoothed_x,
            aim_y=smoothed_y,
            pinch_distance=hand_state.pinch_distance,
        )