/**
 * VisionBird Browser Gesture Controller & Feature Extractor
 */
class BrowserGestureController {
  constructor() {
    this.smoothing = 0.85;
    this.pinchStartThresh = 0.07;
    this.pinchReleaseThresh = 0.10;
    
    this.isGrabbing = false;
    this.wasGrabbing = false;
    this.smoothedPos = null;
  }

  processLandmarks(landmarks) {
    if (!landmarks || landmarks.length < 21) {
      return { detected: false, isGrabbing: false, grabStarted: false, releaseTriggered: false };
    }

    const wrist = landmarks[0];
    const thumbTip = landmarks[4];
    const indexTip = landmarks[8];
    const middleMcp = landmarks[9];

    // Hand scale: wrist to middle finger MCP
    const handScale = Math.hypot(wrist.x - middleMcp.x, wrist.y - middleMcp.y) || 0.2;
    const rawPinch = Math.hypot(indexTip.x - thumbTip.x, indexTip.y - thumbTip.y);
    const normPinch = rawPinch / handScale;

    // Dual-threshold Hysteresis
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

    // Mirror X (1.0 - x)
    const rawX = 1.0 - indexTip.x;
    const rawY = indexTip.y;

    if (!this.smoothedPos) {
      this.smoothedPos = { x: rawX, y: rawY };
    } else {
      this.smoothedPos.x = this.smoothing * rawX + (1.0 - this.smoothing) * this.smoothedPos.x;
      this.smoothedPos.y = this.smoothing * rawY + (1.0 - this.smoothing) * this.smoothedPos.y;
    }

    return {
      detected: true,
      x: this.smoothedPos.x,
      y: this.smoothedPos.y,
      normPinch: normPinch,
      isGrabbing: this.isGrabbing,
      grabStarted: grabStarted,
      releaseTriggered: releaseTriggered
    };
  }

  reset() {
    this.isGrabbing = false;
    this.wasGrabbing = false;
    this.smoothedPos = null;
  }
}
