# VisionBird — Gesture & Control System

## Dual-Threshold Hysteresis

To eliminate hand jitter and pinch flickering near decision boundaries, VisionBird uses dual-threshold hysteresis:

```text
Normalized Pinch Distance
  0.0 ───────────────────────────────────────────> 0.20
       |========== PINCH ACTIVE ==========|
       [Start: 0.06]             [Release: 0.09]
```

- When open, the hand must pinch below **0.06** normalized distance to initiate a grab.
- Once grabbing, the pinch remains active until distance exceeds **0.09**, preventing accidental releases during movement.

## Relative Displacement Control

Direct mapping of the 640x480 webcam frame to the 1200x650 game resolution causes user fatigue. Instead, VisionBird uses relative grab anchor displacement:

$$\Delta x = (x_{current} - x_{anchor}) \cdot \text{Sensitivity}$$
$$\Delta y = (y_{current} - y_{anchor}) \cdot \text{Sensitivity}$$

This allows comfortable micro-hand movements near the user's natural posture.
