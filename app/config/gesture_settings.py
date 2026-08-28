from __future__ import annotations


# ============================================================
# VISIONBIRD GESTURE SETTINGS
# ============================================================

# Hand movement amplification.
GESTURE_SENSITIVITY = 2.2

# Relative pull smoothing.
# Lower = smoother/slower.
# Higher = more responsive.
GESTURE_SMOOTHING = 0.30


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