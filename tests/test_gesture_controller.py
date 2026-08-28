from __future__ import annotations

from app.controls.gesture_controller import GestureController
from app.vision.hand_tracker import HandState


def make_hand_state(
    *,
    detected: bool = True,
    index_tip: tuple[float, float] | None = (0.5, 0.5),
    is_pinching: bool = False,
    pinch_distance: float | None = 0.1,
) -> HandState:
    return HandState(
        detected=detected,
        index_tip=index_tip,
        is_pinching=is_pinching,
        pinch_distance=pinch_distance,
    )


def test_no_hand_returns_empty_control_state() -> None:
    controller = GestureController()

    state = controller.update(
        make_hand_state(
            detected=False,
            index_tip=None,
            pinch_distance=None,
        )
    )

    assert state.hand_detected is False
    assert state.is_grabbing is False
    assert state.grab_started is False
    assert state.release_triggered is False


def test_pinch_starts_grab() -> None:
    controller = GestureController()

    state = controller.update(
        make_hand_state(
            is_pinching=True,
        )
    )

    assert state.hand_detected is True
    assert state.is_grabbing is True
    assert state.grab_started is True
    assert state.release_triggered is False


def test_continuous_pinch_does_not_restart_grab() -> None:
    controller = GestureController()

    controller.update(
        make_hand_state(
            is_pinching=True,
        )
    )

    state = controller.update(
        make_hand_state(
            is_pinching=True,
        )
    )

    assert state.is_grabbing is True
    assert state.grab_started is False


def test_release_triggers_once() -> None:
    controller = GestureController()

    controller.update(
        make_hand_state(
            is_pinching=True,
        )
    )

    state = controller.update(
        make_hand_state(
            is_pinching=False,
        )
    )

    assert state.is_grabbing is False
    assert state.release_triggered is True


def test_position_is_smoothed() -> None:
    controller = GestureController(
        smoothing=0.5,
    )

    controller.update(
        make_hand_state(
            index_tip=(0.0, 0.0),
        )
    )

    state = controller.update(
        make_hand_state(
            index_tip=(1.0, 1.0),
        )
    )

    assert state.aim_x == 0.5
    assert state.aim_y == 0.5


def test_reset_clears_grab_state() -> None:
    controller = GestureController()

    controller.update(
        make_hand_state(
            is_pinching=True,
        )
    )

    controller.reset()

    state = controller.update(
        make_hand_state(
            is_pinching=False,
        )
    )

    assert state.grab_started is False
    assert state.release_triggered is False