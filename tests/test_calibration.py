from __future__ import annotations

from app.vision.calibration import HandCalibrator


def test_calibrator_accumulation_and_finalize():
    calibrator = HandCalibrator(sample_target=5)
    assert calibrator.data.calibrated is False

    for i in range(4):
        done = calibrator.add_sample(0.5, 0.5, 0.05)
        assert done is False

    done = calibrator.add_sample(0.5, 0.5, 0.05)
    assert done is True
    assert calibrator.data.calibrated is True
    assert calibrator.data.neutral_x == 0.5
    assert calibrator.data.neutral_y == 0.5


def test_roi_mapping():
    calibrator = HandCalibrator(sample_target=1)
    calibrator.add_sample(0.5, 0.5, 0.05)

    mapped_x, mapped_y = calibrator.map_to_roi(0.5, 0.5)
    assert 0.0 <= mapped_x <= 1.0
    assert 0.0 <= mapped_y <= 1.0
