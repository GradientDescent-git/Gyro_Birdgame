from __future__ import annotations


# ============================================================
# VISIONBIRD GESTURE SETTINGS
# ============================================================

# Webcam device.
DEFAULT_CAMERA_INDEX = 0


# ------------------------------------------------------------
# HAND MOVEMENT
# ------------------------------------------------------------

# Amplifies relative hand movement.
#
# Higher = faster cursor movement.
# Recommended starting range: 5.0 - 10.0
DEFAULT_SENSITIVITY = 7.0


# Normalized movement smaller than this is ignored.
# Prevents tiny MediaPipe tracking jitter.
DEFAULT_DEAD_ZONE = 0.0015


# GestureController smoothing.
#
# Lower = smoother/slower
# Higher = more responsive
DEFAULT_SMOOTHING = 0.30


# Backward-compatible aliases used elsewhere in the project.
GESTURE_SENSITIVITY = DEFAULT_SENSITIVITY
GESTURE_SMOOTHING = DEFAULT_SMOOTHING


# ============================================================
# SLINGSHOT LIMITS
# ============================================================

# Maximum distance the bird can be pulled.
MAX_PULL_DISTANCE = 150


# Prevent excessive forward movement.
MAX_FORWARD_PULL = 30


# ============================================================
# HAND TRACKING
# ============================================================

# Seconds before an active grab is cancelled
# when the hand disappears.
HAND_LOST_TIMEOUT = 0.75