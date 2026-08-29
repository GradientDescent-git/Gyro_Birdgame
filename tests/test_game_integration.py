from __future__ import annotations

import unittest
from app.game.gesture_bridge import GestureBridge


def test_gesture_bridge_initialization_and_empty_state():
    bridge = GestureBridge(
        screen_width=1200,
        screen_height=650,
        camera_index=0,
        debug_mode=False,
    )

    state = bridge.update()
    assert isinstance(state, dict)
    assert "detected" in state
    assert "x" in state
    assert "y" in state
    assert "pinching" in state

    bridge.close()


def test_gesture_bridge_invalid_args():
    try:
        GestureBridge(screen_width=-100, screen_height=600)
        assert False, "Should raise ValueError for invalid screen width"
    except ValueError:
        pass
