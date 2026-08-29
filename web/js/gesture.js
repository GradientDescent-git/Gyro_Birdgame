/**
 * VisionBird Browser Gesture Controller & Feature Extractor
 * 1:1 Client-Side Port of Python app/controls/gesture_controller.py & gesture_state.py
 */

const GESTURE_CONFIG = {
  PINCH_START_THRESHOLD: 0.06,   // Matching app/config/settings.py
  PINCH_RELEASE_THRESHOLD: 0.09, // Dual-threshold hysteresis
  SMOOTHING_ALPHA: 0.85,         // Low-pass exponential smoothing
  DEAD_ZONE: 0.0015
};

const GestureStateEnum = {
  IDLE: 'IDLE',
  HAND_DETECTED: 'HAND_DETECTED',
  READY: 'READY',
  GRABBING: 'GRABBING',
  PULLING: 'PULLING',
  RELEASED: 'RELEASED',
  LAUNCHED: 'LAUNCHED'
};

class BrowserGestureController {
  constructor() {
    this.smoothing = GESTURE_CONFIG.SMOOTHING_ALPHA;
    this.pinchStartThresh = GESTURE_CONFIG.PINCH_START_THRESHOLD;
    this.pinchReleaseThresh = GESTURE_CONFIG.PINCH_RELEASE_THRESHOLD;

    this.currentState = GestureStateEnum.IDLE;
    this.isGrabbing = false;
    this.wasGrabbing = false;
    this.smoothedPos = null;
  }

  processLandmarks(landmarks) {
    if (!landmarks || landmarks.length < 21) {
      this.reset();
      return {
        detected: false,
        isGrabbing: false,
        grabStarted: false,
        releaseTriggered: false,
        state: GestureStateEnum.IDLE
      };
    }

    const wrist = landmarks[0];
    const thumbTip = landmarks[4];
    const indexTip = landmarks[8];
    const middleMcp = landmarks[9];

    // Scale Normalization: Wrist to Middle Finger MCP reference length S
    const handScale = Math.hypot(wrist.x - middleMcp.x, wrist.y - middleMcp.y) || 0.2;
    const rawPinch = Math.hypot(indexTip.x - thumbTip.x, indexTip.y - thumbTip.y);
    const normPinch = rawPinch / handScale;

    // Dual-Threshold Hysteresis State Logic
    if (!this.isGrabbing) {
      if (normPinch < this.pinchStartThresh) {
        this.isGrabbing = true;
      }
    } else {
      if (normPinch > this.pinchReleaseThresh) {
        this.isGrabbing = false;
      }
    }

    const grabStarted = this.isGrabbing && !this.wasGrabbing;
    const releaseTriggered = this.wasGrabbing && !this.isGrabbing;
    this.wasGrabbing = this.isGrabbing;

    // Position Mirroring & Exponential Low-Pass Filtering
    const rawX = 1.0 - indexTip.x;
    const rawY = indexTip.y;

    if (!this.smoothedPos) {
      this.smoothedPos = { x: rawX, y: rawY };
    } else {
      this.smoothedPos.x = this.smoothing * rawX + (1.0 - this.smoothing) * this.smoothedPos.x;
      this.smoothedPos.y = this.smoothing * rawY + (1.0 - this.smoothing) * this.smoothedPos.y;
    }

    // Update Finite State Machine
    this.updateFSM(true, this.isGrabbing);

    return {
      detected: true,
      x: this.smoothedPos.x,
      y: this.smoothedPos.y,
      normPinch: normPinch,
      isGrabbing: this.isGrabbing,
      grabStarted: grabStarted,
      releaseTriggered: releaseTriggered,
      state: this.currentState
    };
  }

  updateFSM(handDetected, isPinching) {
    if (!handDetected) {
      this.currentState = GestureStateEnum.IDLE;
      return;
    }

    switch (this.currentState) {
      case GestureStateEnum.IDLE:
        this.currentState = GestureStateEnum.HAND_DETECTED;
        break;
      case GestureStateEnum.HAND_DETECTED:
        this.currentState = GestureStateEnum.READY;
        break;
      case GestureStateEnum.READY:
        if (isPinching) this.currentState = GestureStateEnum.GRABBING;
        break;
      case GestureStateEnum.GRABBING:
        this.currentState = isPinching ? GestureStateEnum.PULLING : GestureStateEnum.RELEASED;
        break;
      case GestureStateEnum.PULLING:
        if (!isPinching) this.currentState = GestureStateEnum.RELEASED;
        break;
      case GestureStateEnum.RELEASED:
        this.currentState = GestureStateEnum.LAUNCHED;
        break;
      case GestureStateEnum.LAUNCHED:
        if (!isPinching) this.currentState = GestureStateEnum.READY;
        break;
    }
  }

  reset() {
    this.isGrabbing = false;
    this.wasGrabbing = false;
    this.smoothedPos = null;
    this.currentState = GestureStateEnum.IDLE;
  }
}
