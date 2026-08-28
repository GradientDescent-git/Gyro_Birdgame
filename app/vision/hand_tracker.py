from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np


@dataclass
class HandState:
    detected: bool
    index_tip: Optional[tuple[float, float]] = None
    thumb_tip: Optional[tuple[float, float]] = None
    pinch_distance: Optional[float] = None
    is_pinching: bool = False


class HandTracker:

    def __init__(
        self,
        max_num_hands: int = 1,
        detection_confidence: float = 0.5,
        tracking_confidence: float = 0.5,
        pinch_threshold: float = 0.08,
    ) -> None:

        self.pinch_threshold = pinch_threshold

        self.mp_hands = mp.solutions.hands

        self.mp_draw = mp.solutions.drawing_utils

        self.mp_draw_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            model_complexity=1,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )


    def process(
        self,
        frame: np.ndarray,
    ) -> tuple[np.ndarray, HandState]:

        # ----------------------------------------------------
        # Convert BGR camera frame to RGB for MediaPipe
        # ----------------------------------------------------

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        results = self.hands.process(
            frame_rgb
        )


        hand_state = HandState(
            detected=False
        )


        # ----------------------------------------------------
        # HAND DETECTED
        # ----------------------------------------------------

        if results.multi_hand_landmarks:

            landmarks = results.multi_hand_landmarks[0]


            # Draw hand landmarks
            self.mp_draw.draw_landmarks(
                frame,
                landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw_styles.get_default_hand_landmarks_style(),
                self.mp_draw_styles.get_default_hand_connections_style(),
            )


            # ------------------------------------------------
            # INDEX FINGER TIP
            # ------------------------------------------------

            index_tip = landmarks.landmark[
                self.mp_hands.HandLandmark.INDEX_FINGER_TIP
            ]


            # ------------------------------------------------
            # THUMB TIP
            # ------------------------------------------------

            thumb_tip = landmarks.landmark[
                self.mp_hands.HandLandmark.THUMB_TIP
            ]


            index_point = (
                float(index_tip.x),
                float(index_tip.y),
            )


            thumb_point = (
                float(thumb_tip.x),
                float(thumb_tip.y),
            )


            # ------------------------------------------------
            # PINCH DISTANCE
            # ------------------------------------------------

            pinch_distance = float(
                np.sqrt(
                    (index_tip.x - thumb_tip.x) ** 2
                    +
                    (index_tip.y - thumb_tip.y) ** 2
                )
            )


            is_pinching = (
                pinch_distance < self.pinch_threshold
            )


            # ------------------------------------------------
            # CREATE HAND STATE
            # ------------------------------------------------

            hand_state = HandState(
                detected=True,
                index_tip=index_point,
                thumb_tip=thumb_point,
                pinch_distance=pinch_distance,
                is_pinching=is_pinching,
            )


        return frame, hand_state


    def close(self) -> None:

        self.hands.close()