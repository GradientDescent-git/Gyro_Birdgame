from __future__ import annotations

from app.controls.gesture_state import GestureStateEnum, GestureStateMachine


def test_gesture_state_machine_flow():
    fsm = GestureStateMachine()
    assert fsm.state == GestureStateEnum.IDLE

    # Hand detected -> HAND_DETECTED
    s1 = fsm.update(hand_detected=True, is_pinching=False)
    assert s1 == GestureStateEnum.HAND_DETECTED

    # Next frame -> READY
    s2 = fsm.update(hand_detected=True, is_pinching=False)
    assert s2 == GestureStateEnum.READY

    # Pinch -> GRABBING
    s3 = fsm.update(hand_detected=True, is_pinching=True)
    assert s3 == GestureStateEnum.GRABBING

    # Hold pinch -> PULLING
    s4 = fsm.update(hand_detected=True, is_pinching=True)
    assert s4 == GestureStateEnum.PULLING

    # Release pinch -> RELEASED
    s5 = fsm.update(hand_detected=True, is_pinching=False)
    assert s5 == GestureStateEnum.RELEASED

    # Next frame -> LAUNCHED
    s6 = fsm.update(hand_detected=True, is_pinching=False)
    assert s6 == GestureStateEnum.LAUNCHED

    # Hand lost -> IDLE
    s7 = fsm.update(hand_detected=False, is_pinching=False)
    assert s7 == GestureStateEnum.IDLE
