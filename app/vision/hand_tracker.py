from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np

try:
    import mediapipe as mp
    if hasattr(mp, "solutions") and hasattr(mp.solutions, "hands"):
        mp_hands = mp.solutions.hands
        mp_draw = mp.solutions.drawing_utils
        mp_draw_styles = mp.solutions.drawing_styles
    else:
        import mediapipe.python.solutions.hands as mp_hands
        import mediapipe.python.solutions.drawing_utils as mp_draw
        import mediapipe.python.solutions.drawing_styles as mp_draw_styles
except Exception:
    mp_hands = None
    mp_draw = None
    mp_draw_styles = None

from app.vision.features import FeatureExtractor, FeatureVector, Point2D


@dataclass
class HandState:
    detected: bool = False
    handedness: str = "Unknown"
    index_tip: Optional[Tuple[float, float]] = None
    thumb_tip: Optional[Tuple[float, float]] = None
    hand_center: Optional[Tuple[float, float]] = None
    pinch_distance: Optional[float] = None
    normalized_pinch_distance: Optional[float] = None
    is_pinching: bool = False
    confidence: float = 0.0
    hand_scale: float = 1.0


class HandTracker:
    """
    MediaPipe-backed robust hand tracking engine.
    Converts RGB camera frames into clean, structured HandState objects.
    """

    def __init__(
        self,
        max_num_hands: int = 1,
        detection_confidence: float = 0.5,
        tracking_confidence: float = 0.5,
        pinch_threshold: float = 0.08,
    ) -> None:
        self.pinch_threshold = pinch_threshold
        self.feature_extractor = FeatureExtractor()

        self.mp_hands = mp_hands
        self.mp_draw = mp_draw
        self.mp_draw_styles = mp_draw_styles

        if self.mp_hands is not None:
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=max_num_hands,
                model_complexity=1,
                min_detection_confidence=detection_confidence,
                min_tracking_confidence=tracking_confidence,
            )
        else:
            self.hands = None

    def process(self, frame: np.ndarray) -> Tuple[np.ndarray, HandState]:
        if frame is None or frame.size == 0 or self.hands is None:
            return frame, HandState(detected=False)

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)
        except Exception:
            return frame, HandState(detected=False)

        if not results.multi_hand_landmarks:
            return frame, HandState(detected=False)

        landmarks = results.multi_hand_landmarks[0]

        # Extract handedness if available
        handedness_label = "Right"
        score = 0.9
        if results.multi_handedness and len(results.multi_handedness) > 0:
            handedness_info = results.multi_handedness[0].classification[0]
            handedness_label = handedness_info.label
            score = float(handedness_info.score)

        # Draw hand landmarks cleanly
        if self.mp_draw and self.mp_draw_styles and self.mp_hands:
            self.mp_draw.draw_landmarks(
                frame,
                landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw_styles.get_default_hand_landmarks_style(),
                self.mp_draw_styles.get_default_hand_connections_style(),
            )

        # Feature Extraction
        feature_vec: FeatureVector = self.feature_extractor.extract(
            landmarks.landmark, handedness_label=handedness_label, score=score
        )

        index_pt = (feature_vec.index_tip.x, feature_vec.index_tip.y) if feature_vec.index_tip else None
        thumb_pt = (feature_vec.thumb_tip.x, feature_vec.thumb_tip.y) if feature_vec.thumb_tip else None
        center_pt = (feature_vec.hand_center.x, feature_vec.hand_center.y) if feature_vec.hand_center else None

        is_pinching = feature_vec.raw_pinch_distance < self.pinch_threshold

        hand_state = HandState(
            detected=True,
            handedness=handedness_label,
            index_tip=index_pt,
            thumb_tip=thumb_pt,
            hand_center=center_pt,
            pinch_distance=feature_vec.raw_pinch_distance,
            normalized_pinch_distance=feature_vec.normalized_pinch_distance,
            is_pinching=is_pinching,
            confidence=score,
            hand_scale=feature_vec.hand_scale,
        )

        return frame, hand_state

    def close(self) -> None:
        if self.hands is not None:
            self.hands.close()