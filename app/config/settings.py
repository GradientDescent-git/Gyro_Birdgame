from __future__ import annotations

"""
VisionBird Configuration Settings
"""

DEFAULT_CAMERA_INDEX = 0

# Movement Sensitivity & Deadzone
DEFAULT_SENSITIVITY = 12.0
DEFAULT_DEAD_ZONE = 0.0005

DEFAULT_SMOOTHING = 0.85

# Backward Compatibility
GESTURE_SENSITIVITY = DEFAULT_SENSITIVITY
GESTURE_SMOOTHING = DEFAULT_SMOOTHING

# Forgiving Pinch Thresholds (Normalized Distance)
PINCH_START_THRESHOLD = 0.12
PINCH_RELEASE_THRESHOLD = 0.16
DEBOUNCE_FRAMES = 1

# Slingshot Limits
MAX_PULL_DISTANCE = 200
MAX_FORWARD_PULL = 50

# Timeouts
HAND_LOST_TIMEOUT = 1.0

# Display Resolution
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 650
