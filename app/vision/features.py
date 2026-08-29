from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Point2D:
    x: float
    y: float

    def distance_to(self, other: Point2D) -> float:
        return math.hypot(self.x - other.x, self.y - other.y)


@dataclass
class FeatureVector:
    """Normalized geometric features extracted from 21 MediaPipe hand landmarks."""

    hand_detected: bool = False
    handedness: str = "Unknown"
    confidence: float = 0.0

    index_tip: Optional[Point2D] = None
    thumb_tip: Optional[Point2D] = None
    wrist: Optional[Point2D] = None
    hand_center: Optional[Point2D] = None

    raw_pinch_distance: float = 0.0
    hand_scale: float = 1.0
    normalized_pinch_distance: float = 0.0

    is_open_hand: bool = False
    is_fist: bool = False


class FeatureExtractor:
    """
    Extracts scale-invariant normalized geometric features from MediaPipe hand landmarks.
    
    Mathematical justification:
    Raw pixel distance between thumb and index finger varies based on hand distance from camera.
    By normalizing by the hand scale (wrist to middle finger MCP distance), the pinch metric
    remains scale-invariant regardless of user positioning.
    """

    def __init__(self, default_hand_scale: float = 0.2) -> None:
        self.default_hand_scale = default_hand_scale

    def extract(self, landmarks_list: Any, handedness_label: str = "Right", score: float = 1.0) -> FeatureVector:
        if not landmarks_list or len(landmarks_list) < 21:
            return FeatureVector()

        # Extract key landmarks (MediaPipe landmark indices)
        # 0: WRIST, 4: THUMB_TIP, 8: INDEX_FINGER_TIP, 9: MIDDLE_FINGER_MCP, 12: MIDDLE_FINGER_TIP
        wrist = Point2D(float(landmarks_list[0].x), float(landmarks_list[0].y))
        thumb_tip = Point2D(float(landmarks_list[4].x), float(landmarks_list[4].y))
        index_tip = Point2D(float(landmarks_list[8].x), float(landmarks_list[8].y))
        middle_mcp = Point2D(float(landmarks_list[9].x), float(landmarks_list[9].y))
        middle_tip = Point2D(float(landmarks_list[12].x), float(landmarks_list[12].y))

        # Hand scale: Wrist to Middle Finger MCP reference length
        hand_scale = wrist.distance_to(middle_mcp)
        if hand_scale < 1e-4:
            hand_scale = self.default_hand_scale

        # Raw distance between index tip and thumb tip
        raw_pinch_dist = index_tip.distance_to(thumb_tip)

        # Scale-invariant normalized pinch distance
        norm_pinch_dist = raw_pinch_dist / hand_scale

        # Hand center centroid
        center = Point2D((wrist.x + middle_mcp.x) / 2.0, (wrist.y + middle_mcp.y) / 2.0)

        # Check if open hand (all fingertips extended far from wrist)
        middle_dist = wrist.distance_to(middle_tip)
        is_open_hand = (middle_dist / hand_scale) > 1.4

        return FeatureVector(
            hand_detected=True,
            handedness=handedness_label,
            confidence=score,
            index_tip=index_tip,
            thumb_tip=thumb_tip,
            wrist=wrist,
            hand_center=center,
            raw_pinch_distance=raw_pinch_dist,
            hand_scale=hand_scale,
            normalized_pinch_distance=norm_pinch_dist,
            is_open_hand=is_open_hand,
        )
