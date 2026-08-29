/**
 * VisionBird HTML5 Physics Game Engine
 */
class VisionBirdGame {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.ctx = this.canvas.getContext('2d');
    
    this.slingshot = { x: 200, y: 480 };
    this.bird = { x: 200, y: 480, vx: 0, vy: 0, radius: 18, launched: false, grabbing: false };
    this.pigs = [
      { x: 900, y: 500, radius: 22, alive: true },
      { x: 980, y: 500, radius: 22, alive: true },
      { x: 940, y: 420, radius: 22, alive: true }
    ];
    this.blocks = [
      { x: 880, y: 520, w: 140, h: 20, hit: false },
      { x: 930, y: 440, w: 100, h: 20, hit: false }
    ];

    this.score = 0;
    this.level = 1;
    this.gestureController = new BrowserGestureController();
    this.visionTracker = null;

    this.mouse = { x: 200, y: 480, isDown: false };
    this.setupEvents();
  }

  setupEvents() {
    // Mouse fallback handlers
    this.canvas.addEventListener('mousedown', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      this.mouse.x = (e.clientX - rect.left) * (this.canvas.width / rect.width);
      this.mouse.y = (e.clientY - rect.top) * (this.canvas.height / rect.height);
      this.mouse.isDown = true;
    });

    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      this.mouse.x = (e.clientX - rect.left) * (this.canvas.width / rect.width);
      this.mouse.y = (e.clientY - rect.top) * (this.canvas.height / rect.height);
    });

    window.addEventListener('mouseup', () => {
      if (this.mouse.isDown && !this.bird.launched) {
        this.launchBirdFrom(this.mouse.x, this.mouse.y);
      }
      this.mouse.isDown = false;
    });

    document.getElementById('btn-camera').addEventListener('click', async () => {
      if (!this.visionTracker) {
        this.visionTracker = new VisionTracker((landmarks) => this.handleGestureInput(landmarks));
        const ok = await this.visionTracker.init();
        if (ok) {
          document.getElementById('hud-status').innerText = "Controls: Webcam Active | MediaPipe Tracking";
          document.getElementById('hud-status').style.color = "#2ed573";
        }
      }
    });

    document.getElementById('btn-restart').addEventListener('click', () => this.resetLevel());
  }

  handleGestureInput(landmarks) {
    const res = this.gestureController.processLandmarks(landmarks);
    if (!res.detected) return;

    const gameX = res.x * this.canvas.width;
    const gameY = res.y * this.canvas.height;

    if (!this.bird.launched) {
      if (res.grabStarted || (res.isGrabbing && !this.bird.grabbing)) {
        const dist = Math.hypot(gameX - this.slingshot.x, gameY - this.slingshot.y);
        if (dist < 100) {
          this.bird.grabbing = true;
        }
      }

      if (this.bird.grabbing) {
        if (res.isGrabbing) {
          // Clamp pull distance
          const dx = gameX - this.slingshot.x;
          const dy = gameY - this.slingshot.y;
          const pullDist = Math.hypot(dx, dy);
          const maxPull = 120;
          if (pullDist > maxPull) {
            const angle = Math.atan2(dy, dx);
            this.bird.x = this.slingshot.x + Math.cos(angle) * maxPull;
            this.bird.y = this.slingshot.y + Math.sin(angle) * maxPull;
          } else {
            this.bird.x = gameX;
            this.bird.y = gameY;
          }
        } else if (res.releaseTriggered) {
          this.launchBirdFrom(this.bird.x, this.bird.y);
          this.bird.grabbing = false;
        }
      }
    }
  }

  launchBirdFrom(x, y) {
    const dx = this.slingshot.x - x;
    const dy = this.slingshot.y - y;
    this.bird.vx = dx * 0.18;
    this.bird.vy = dy * 0.18;
    this.bird.launched = true;
  }

  resetLevel() {
    this.bird = { x: 200, y: 480, vx: 0, vy: 0, radius: 18, launched: false, grabbing: false };
    this.pigs.forEach(p => p.alive = true);
    this.blocks.forEach(b => b.hit = false);
    this.score = 0;
  }

  updatePhysics() {
    // Mouse drag handling when webcam is disabled
    if (this.mouse.isDown && !this.bird.launched && !this.bird.grabbing) {
      const dx = this.mouse.x - this.slingshot.x;
      const dy = this.mouse.y - this.slingshot.y;
      const pullDist = Math.hypot(dx, dy);
      const maxPull = 120;
      if (pullDist > maxPull) {
        const angle = Math.atan2(dy, dx);
        this.bird.x = this.slingshot.x + Math.cos(angle) * maxPull;
        this.bird.y = this.slingshot.y + Math.sin(angle) * maxPull;
      } else {
        this.bird.x = this.mouse.x;
        this.bird.y = this.mouse.y;
      }
    }

    if (this.bird.launched) {
      this.bird.x += this.bird.vx;
      this.bird.y += this.bird.vy;
      this.bird.vy += 0.45; // Gravity

      // Ground collision
      if (this.bird.y + this.bird.radius >= 540) {
        this.bird.y = 540 - this.bird.radius;
        this.bird.vx *= 0.6;
        this.bird.vy *= -0.3;
      }

      // Pig collision check
      this.pigs.forEach((pig) => {
        if (pig.alive) {
          const dist = Math.hypot(this.bird.x - pig.x, this.bird.y - pig.y);
          if (dist < this.bird.radius + pig.radius) {
            pig.alive = false;
            this.score += 5000;
          }
        }
      });
    }
  }

  render() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Sky background gradient
    const skyGrad = this.ctx.createLinearGradient(0, 0, 0, 540);
    skyGrad.addColorStop(0, '#70a1ff');
    skyGrad.addColorStop(1, '#eccc68');
    this.ctx.fillStyle = skyGrad;
    this.ctx.fillRect(0, 0, this.canvas.width, 540);

    // Ground
    this.ctx.fillStyle = '#2ed573';
    this.ctx.fillRect(0, 540, this.canvas.width, 110);
    this.ctx.fillStyle = '#747d8c';
    this.ctx.fillRect(0, 550, this.canvas.width, 100);

    // Slingshot band
    if (!this.bird.launched) {
      this.ctx.strokeStyle = '#301934';
      this.ctx.lineWidth = 6;
      this.ctx.beginPath();
      this.ctx.moveTo(185, 470);
      this.ctx.lineTo(this.bird.x, this.bird.y);
      this.ctx.lineTo(215, 470);
      this.ctx.stroke();
    }

    // Slingshot post
    this.ctx.fillStyle = '#8B4513';
    this.ctx.fillRect(193, 470, 14, 70);

    // Blocks
    this.ctx.fillStyle = '#d2dae2';
    this.blocks.forEach(b => {
      this.ctx.fillRect(b.x, b.y, b.w, b.h);
      this.ctx.strokeRect(b.x, b.y, b.w, b.h);
    });

    // Pigs
    this.pigs.forEach(pig => {
      if (pig.alive) {
        this.ctx.fillStyle = '#2ed573';
        this.ctx.beginPath();
        this.ctx.arc(pig.x, pig.y, pig.radius, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.strokeStyle = '#1e8449';
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
        // Snout
        this.ctx.fillStyle = '#26de81';
        this.ctx.beginPath();
        this.ctx.arc(pig.x, pig.y + 2, 9, 0, 2 * Math.PI);
        this.ctx.fill();
      }
    });

    // Bird (Red Bird)
    this.ctx.fillStyle = '#ff4757';
    this.ctx.beginPath();
    this.ctx.arc(this.bird.x, this.bird.y, this.bird.radius, 0, 2 * Math.PI);
    this.ctx.fill();
    this.ctx.strokeStyle = '#2f3542';
    this.ctx.lineWidth = 2;
    this.ctx.stroke();
    // Beak
    this.ctx.fillStyle = '#ffa502';
    this.ctx.beginPath();
    this.ctx.moveTo(this.bird.x + 8, this.bird.y - 2);
    this.ctx.lineTo(this.bird.x + 22, this.bird.y + 3);
    this.ctx.lineTo(this.bird.x + 8, this.bird.y + 8);
    this.ctx.closePath();
    this.ctx.fill();

    // HUD Text
    this.ctx.fillStyle = '#ffffff';
    this.ctx.font = 'bold 22px Segoe UI';
    this.ctx.fillText(`SCORE: ${this.score}`, 30, 40);
    this.ctx.fillText(`LEVEL: ${this.level}`, 30, 75);
  }

  loop() {
    this.updatePhysics();
    this.render();
    requestAnimationFrame(() => this.loop());
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const game = new VisionBirdGame();
  game.loop();
});
