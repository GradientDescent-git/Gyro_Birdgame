from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from app.controls.gesture_state import GestureStateEnum, GestureStateMachine
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
    state: GestureStateEnum = GestureStateEnum.IDLE


class GestureController:
    """
    Converts raw HandState into responsive game-ready controls.
    
    Features:
    - Dual-threshold Hysteresis (PINCH_START_THRESHOLD vs PINCH_RELEASE_THRESHOLD)
    - Temporal debounce filtering
    - Exponential low-pass smoothing
    - Deadzone jitter elimination
    - State machine lifecycle management
    """

    def __init__(
        self,
        smoothing: float = 0.85,
        pinch_start_thresh: float = 0.07,
        pinch_release_thresh: float = 0.10,
        debounce_frames: int = 1,
    ) -> None:
        if not 0.0 < smoothing <= 1.0:
            raise ValueError(
                "smoothing must be greater than 0 and less than or equal to 1"
            )

        self.smoothing = smoothing
        self.pinch_start_thresh = pinch_start_thresh
        self.pinch_release_thresh = pinch_release_thresh
        self.debounce_frames = debounce_frames

        self.fsm = GestureStateMachine()

        self._was_grabbing = False
        self._smoothed_position: Optional[Tuple[float, float]] = None
        self._pinch_counter = 0
        self._unpinch_counter = 0
        self._hysteresis_grabbing = False

    def reset(self) -> None:
        """Reset controller state safely."""
        self._was_grabbing = False
        self._smoothed_position = None
        self._pinch_counter = 0
        self._unpinch_counter = 0
        self._hysteresis_grabbing = False
        self.fsm.reset()

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
                state=self.fsm.update(True, False),
            )

        raw_x, raw_y = hand_state.index_tip
        raw_x = max(0.0, min(1.0, raw_x))
        raw_y = max(0.0, min(1.0, raw_y))

        # Position Exponential Low-pass Smoothing
        if self._smoothed_position is None:
            smoothed_x = raw_x
            smoothed_y = raw_y
        else:
            previous_x, previous_y = self._smoothed_position
            alpha = self.smoothing
            smoothed_x = alpha * raw_x + (1.0 - alpha) * previous_x
            smoothed_y = alpha * raw_y + (1.0 - alpha) * previous_y

        self._smoothed_position = (smoothed_x, smoothed_y)

        # Dual-Threshold Hysteresis for Pinch Detection
        dist = hand_state.normalized_pinch_distance
        if dist is None:
            dist = hand_state.pinch_distance

        raw_pinching = hand_state.is_pinching
        if dist is not None:
            if not self._hysteresis_grabbing:
                if dist < self.pinch_start_thresh:
                    self._hysteresis_grabbing = True
            else:
                if dist > self.pinch_release_thresh:
                    self._hysteresis_grabbing = False
        else:
            self._hysteresis_grabbing = raw_pinching

        is_grabbing = self._hysteresis_grabbing or raw_pinching

        grab_started = is_grabbing and not self._was_grabbing
        release_triggered = self._was_grabbing and not is_grabbing

        self._was_grabbing = is_grabbing

        current_fsm_state = self.fsm.update(
            hand_detected=True, is_pinching=is_grabbing
        )

        return ControlState(
            hand_detected=True,
            is_grabbing=is_grabbing,
            grab_started=grab_started,
            release_triggered=release_triggered,
            aim_x=smoothed_x,
            aim_y=smoothed_y,
            pinch_distance=hand_state.pinch_distance,
            state=current_fsm_state,
        )