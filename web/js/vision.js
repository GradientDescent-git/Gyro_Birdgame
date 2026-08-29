/**
 * VisionBird Web MediaPipe Hand Tracking Setup
 */
class VisionTracker {
  constructor(onResultsCallback) {
    this.onResultsCallback = onResultsCallback;
    this.videoElement = document.getElementById('webcam');
    this.previewCanvas = document.getElementById('cvPreview');
    this.previewCtx = this.previewCanvas.getContext('2d');
    this.hands = null;
    this.camera = null;
  }

  async init() {
    this.hands = new Hands({
      locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
    });

    this.hands.setOptions({
      maxNumHands: 1,
      modelComplexity: 1,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });

    this.hands.onResults((results) => this.handleResults(results));

    try {
      this.camera = new Camera(this.videoElement, {
        onFrame: async () => {
          await this.hands.send({ image: this.videoElement });
        },
        width: 320,
        height: 240
      });
      await this.camera.start();
      return true;
    } catch (err) {
      console.warn("Webcam access failed or denied:", err);
      return false;
    }
  }

  handleResults(results) {
    // Render debug preview
    this.previewCtx.save();
    this.previewCtx.clearRect(0, 0, this.previewCanvas.width, this.previewCanvas.height);
    this.previewCtx.drawImage(results.image, 0, 0, this.previewCanvas.width, this.previewCanvas.height);

    let landmarks = null;
    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      landmarks = results.multiHandLandmarks[0];
      // Draw key landmarks
      this.previewCtx.fillStyle = '#00FF00';
      landmarks.forEach((pt) => {
        this.previewCtx.beginPath();
        this.previewCtx.arc(pt.x * this.previewCanvas.width, pt.y * this.previewCanvas.height, 3, 0, 2 * Math.PI);
        this.previewCtx.fill();
      });
    }
    this.previewCtx.restore();

    if (this.onResultsCallback) {
      this.onResultsCallback(landmarks);
    }
  }
}
