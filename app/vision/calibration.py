from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class CalibrationData:
    """Stores calibration parameters for hand positioning and gesture sensitivity."""

    calibrated: bool = False
    neutral_x: float = 0.5
    neutral_y: float = 0.5
    roi_min_x: float = 0.15
    roi_max_x: float = 0.85
    roi_min_y: float = 0.15
    roi_max_y: float = 0.85
    pinch_baseline: float = 0.45


class HandCalibrator:
    """
    Lightweight, progressive calibration system.
    Determines neutral hand rest position, active control ROI, and pinch baseline.
    """

    def __init__(self, sample_target: int = 30) -> None:
        self.sample_target = sample_target
        self._samples_x: list[float] = []
        self._samples_y: list[float] = []
        self._pinch_samples: list[float] = []
        self.data = CalibrationData()

    def reset(self) -> None:
        self._samples_x.clear()
        self._samples_y.clear()
        self._pinch_samples.clear()
        self.data = CalibrationData()

    def add_sample(self, norm_x: float, norm_y: float, norm_pinch_dist: float) -> bool:
        """
        Collect calibration sample. Returns True when calibration completes.
        """
        self._samples_x.append(norm_x)
        self._samples_y.append(norm_y)
        self._pinch_samples.append(norm_pinch_dist)

        if len(self._samples_x) >= self.sample_target:
            self._finalize()
            return True
        return False

    def _finalize(self) -> None:
        avg_x = sum(self._samples_x) / len(self._samples_x)
        avg_y = sum(self._samples_y) / len(self._samples_y)
        avg_pinch = sum(self._pinch_samples) / len(self._pinch_samples)

        margin_x = 0.35
        margin_y = 0.35

        roi_min_x = max(0.0, avg_x - margin_x)
        roi_max_x = min(1.0, avg_x + margin_x)
        roi_min_y = max(0.0, avg_y - margin_y)
        roi_max_y = min(1.0, avg_y + margin_y)

        self.data = CalibrationData(
            calibrated=True,
            neutral_x=avg_x,
            neutral_y=avg_y,
            roi_min_x=roi_min_x,
            roi_max_x=roi_max_x,
            roi_min_y=roi_min_y,
            roi_max_y=roi_max_y,
            pinch_baseline=avg_pinch,
        )

    def map_to_roi(self, x: float, y: float) -> Tuple[float, float]:
        """Maps normalized camera point (0-1) to ROI bounded normalized space (0-1)."""
        d = self.data
        dx = d.roi_max_x - d.roi_min_x
        dy = d.roi_max_y - d.roi_min_y

        if dx < 1e-4 or dy < 1e-4:
            return x, y

        mapped_x = (x - d.roi_min_x) / dx
        mapped_y = (y - d.roi_min_y) / dy

        clamped_x = max(0.0, min(1.0, mapped_x))
        clamped_y = max(0.0, min(1.0, mapped_y))
        return clamped_x, clamped_y
