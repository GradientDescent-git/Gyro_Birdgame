from __future__ import annotations

import numpy as np
from app.controls.gesture_controller import GestureController
from app.controls.gesture_state import GestureStateEnum
from app.vision.features import FeatureExtractor, Point2D
from app.vision.hand_tracker import HandState, HandTracker


def test_full_synthetic_pipeline_integration():
    """
    End-to-End Pipeline Integration Test:
    Synthetic Frame -> Landmark Processing -> Feature Extractor -> Hysteresis FSM -> Gesture State.
    """
    # 1. Initialize Pipeline Modules
    extractor = FeatureExtractor()
    controller = GestureController(smoothing=0.85, pinch_start_thresh=0.06, pinch_release_thresh=0.09)

    # 2. Simulate Synthetic Hand Landmarks
    class DummyPt:
        def __init__(self, x: float, y: float, z: float = 0.0):
            self.x = x
            self.y = y
            self.z = z

    # 21 Synthetic Landmarks
    landmarks = [DummyPt(0.5, 0.5) for _ in range(21)]
    landmarks[0] = DummyPt(0.5, 0.8)   # Wrist
    landmarks[9] = DummyPt(0.5, 0.5)   # Middle MCP (Hand scale S = 0.3)
    landmarks[4] = DummyPt(0.5, 0.3)   # Thumb tip
    landmarks[8] = DummyPt(0.5, 0.31)  # Index tip (Pinch dist = 0.01, norm = 0.033 < 0.06 -> START PINCH)

    # 3. Extract Feature Vector
    vec = extractor.extract(landmarks, handedness_label="Right", score=0.98)
    assert vec.hand_detected is True
    assert vec.normalized_pinch_distance < 0.06

    # 4. Construct HandState
    hand_state = HandState(
        detected=True,
        handedness=vec.handedness,
        index_tip=(vec.index_tip.x, vec.index_tip.y),
        thumb_tip=(vec.thumb_tip.x, vec.thumb_tip.y),
        pinch_distance=vec.raw_pinch_distance,
        normalized_pinch_distance=vec.normalized_pinch_distance,
        is_pinching=(vec.normalized_pinch_distance < 0.06),
        confidence=vec.confidence,
    )

    # 5. Process through Controller FSM
    ctrl_state_1 = controller.update(hand_state)
    assert ctrl_state_1.hand_detected is True
    assert ctrl_state_1.is_grabbing is True
    assert ctrl_state_1.grab_started is True
    assert ctrl_state_1.state in (GestureStateEnum.HAND_DETECTED, GestureStateEnum.GRABBING)

    # 6. Simulate Finger Release (norm pinch > 0.09)
    landmarks[8] = DummyPt(0.5, 0.38) # Index tip moved away (norm pinch = 0.08 / 0.3 = 0.266 > 0.09 -> RELEASE)
    vec_released = extractor.extract(landmarks, handedness_label="Right", score=0.98)
    hand_state_released = HandState(
        detected=True,
        index_tip=(vec_released.index_tip.x, vec_released.index_tip.y),
        thumb_tip=(vec_released.thumb_tip.x, vec_released.thumb_tip.y),
        pinch_distance=vec_released.raw_pinch_distance,
        normalized_pinch_distance=vec_released.normalized_pinch_distance,
        is_pinching=False,
    )

    ctrl_state_2 = controller.update(hand_state_released)
    assert ctrl_state_2.is_grabbing is False
    assert ctrl_state_2.release_triggered is True
