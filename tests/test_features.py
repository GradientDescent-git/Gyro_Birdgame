from __future__ import annotations

import math
from dataclasses import dataclass

from app.vision.features import FeatureExtractor, Point2D


@dataclass
class DummyLandmark:
    x: float
    y: float
    z: float = 0.0


def test_point2d_distance():
    p1 = Point2D(0.0, 0.0)
    p2 = Point2D(3.0, 4.0)
    assert math.isclose(p1.distance_to(p2), 5.0)


def test_feature_extractor_empty_landmarks():
    extractor = FeatureExtractor()
    vec = extractor.extract([])
    assert vec.hand_detected is False


def test_feature_extractor_valid_landmarks():
    extractor = FeatureExtractor()
    # Create 21 dummy landmarks
    landmarks = [DummyLandmark(0.5, 0.5) for _ in range(21)]
    # Landmark 0: Wrist at (0.5, 0.9)
    landmarks[0] = DummyLandmark(0.5, 0.9)
    # Landmark 4: Thumb tip at (0.4, 0.3)
    landmarks[4] = DummyLandmark(0.4, 0.3)
    # Landmark 8: Index tip at (0.45, 0.3)
    landmarks[8] = DummyLandmark(0.45, 0.3)
    # Landmark 9: Middle MCP at (0.5, 0.5)
    landmarks[9] = DummyLandmark(0.5, 0.5)
    # Landmark 12: Middle tip at (0.5, 0.1)
    landmarks[12] = DummyLandmark(0.5, 0.1)

    vec = extractor.extract(landmarks, handedness_label="Left", score=0.95)

    assert vec.hand_detected is True
    assert vec.handedness == "Left"
    assert vec.confidence == 0.95
    assert math.isclose(vec.hand_scale, 0.4)
    assert math.isclose(vec.raw_pinch_distance, 0.05)
    assert math.isclose(vec.normalized_pinch_distance, 0.125)
    assert vec.is_open_hand is True
