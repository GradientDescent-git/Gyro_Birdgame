from __future__ import annotations

from enum import Enum, auto


class GestureStateEnum(Enum):
    IDLE = auto()
    HAND_DETECTED = auto()
    READY = auto()
    GRABBING = auto()
    PULLING = auto()
    RELEASED = auto()
    LAUNCHED = auto()


class GestureStateMachine:
    """
    Finite State Machine governing gesture lifecycle.
    Prevents accidental launch, duplicate triggers, and flicker state transitions.
    """

    def __init__(self) -> None:
        self.state = GestureStateEnum.IDLE

    def reset(self) -> None:
        self.state = GestureStateEnum.IDLE

    def update(
        self, hand_detected: bool, is_pinching: bool, is_near_bird: bool = True
    ) -> GestureStateEnum:
        if not hand_detected:
            self.state = GestureStateEnum.IDLE
            return self.state

        current = self.state

        if current == GestureStateEnum.IDLE:
            self.state = GestureStateEnum.HAND_DETECTED
        elif current == GestureStateEnum.HAND_DETECTED:
            if is_near_bird:
                self.state = GestureStateEnum.READY
        elif current == GestureStateEnum.READY:
            if is_pinching:
                self.state = GestureStateEnum.GRABBING
        elif current == GestureStateEnum.GRABBING:
            if is_pinching:
                self.state = GestureStateEnum.PULLING
            else:
                self.state = GestureStateEnum.RELEASED
        elif current == GestureStateEnum.PULLING:
            if not is_pinching:
                self.state = GestureStateEnum.RELEASED
        elif current == GestureStateEnum.RELEASED:
            self.state = GestureStateEnum.LAUNCHED
        elif current == GestureStateEnum.LAUNCHED:
            if not is_pinching:
                self.state = GestureStateEnum.READY

        return self.state
