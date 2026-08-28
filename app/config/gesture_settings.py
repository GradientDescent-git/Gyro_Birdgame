from __future__ import annotations


# ============================================================
# VISIONBIRD GESTURE SETTINGS
# ============================================================

# Webcam index.
DEFAULT_CAMERA_INDEX = 0


# ============================================================
# GESTURE MOVEMENT
# ============================================================

# Higher = faster cursor movement.
# Recommended starting value for VisionBird.
DEFAULT_SENSITIVITY = 4.5

# Ignore tiny hand-tracking jitter.
DEFAULT_DEAD_ZONE = 0.0015

# Higher = more responsive.
# 1.0 = no smoothing.
DEFAULT_SMOOTHING = 0.85


# ============================================================
# BACKWARD-COMPATIBLE GAME SETTINGS
# ============================================================

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