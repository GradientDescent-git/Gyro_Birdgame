from __future__ import annotations

"""
VisionBird Configuration Settings
"""

DEFAULT_CAMERA_INDEX = 0

# Movement Sensitivity & Deadzone
# High sensitivity (10.0x) for effortless hand-movement control
DEFAULT_SENSITIVITY = 10.0
DEFAULT_DEAD_ZONE = 0.001

DEFAULT_SMOOTHING = 0.85

# Backward Compatibility
GESTURE_SENSITIVITY = DEFAULT_SENSITIVITY
GESTURE_SMOOTHING = DEFAULT_SMOOTHING

# Hysteresis Pinch Thresholds (Normalized Distance)
PINCH_START_THRESHOLD = 0.07
PINCH_RELEASE_THRESHOLD = 0.11
DEBOUNCE_FRAMES = 1

# Slingshot Limits
MAX_PULL_DISTANCE = 180
MAX_FORWARD_PULL = 40

# Timeouts
HAND_LOST_TIMEOUT = 0.75

# Display Resolution
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 650
