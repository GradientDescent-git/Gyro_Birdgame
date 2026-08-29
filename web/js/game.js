/**
 * VisionBird Authentic HTML5 Angry Birds Physics Engine & Gesture Controller
 * Features: Authentic Sprites, Trajectory Projection, Wood/Stone Structural Columns & Beams, 
 * Web Audio Sound Synth, Multi-Level Progression (Levels 1-3), Stars, and MediaPipe Hand Control.
 */
class VisionBirdGame {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.ctx = this.canvas.getContext('2d');

    // Load authentic Angry Birds sprite images
    this.assets = {
      background: new Image(),
      bird: new Image(),
      sling: new Image(),
      pig: new Image(),
      wood: new Image(),
      column: new Image(),
      stars: new Image()
    };

    this.assets.background.src = 'web/images/background3.png';
    this.assets.bird.src = 'web/images/red-bird3.png';
    this.assets.sling.src = 'web/images/sling-3.png';
    this.assets.pig.src = 'web/images/pig_failed.png';
    this.assets.wood.src = 'web/images/wood.png';
    this.assets.column.src = 'web/images/column.png';
    this.assets.stars.src = 'web/images/stars-edited.png';

    // Audio Synthesizer using Web Audio API
    this.audioCtx = null;

    this.slingshot = { x: 200, y: 460 };
    this.bird = { x: 200, y: 460, vx: 0, vy: 0, radius: 20, launched: false, grabbing: false };

    this.level = 1;
    this.score = 0;
    this.highScore = 0;
    this.birdsRemaining = 4;

    this.pigs = [];
    this.blocks = [];
    this.particles = [];

    this.gestureController = new BrowserGestureController();
    this.visionTracker = null;

    this.mouse = { x: 200, y: 460, isDown: false };
    
    this.loadLevel(this.level);
    this.setupEvents();
  }

  initAudio() {
    if (!this.audioCtx) {
      this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
  }

  playSound(freq, type = 'sine', duration = 0.15) {
    if (!this.audioCtx) return;
    try {
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.audioCtx.currentTime);
      gain.gain.setValueAtTime(0.2, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + duration);
    } catch (e) {}
  }

  loadLevel(levelNum) {
    this.level = levelNum;
    this.bird = { x: 200, y: 460, vx: 0, vy: 0, radius: 20, launched: false, grabbing: false };
    this.birdsRemaining = 4;
    this.particles = [];

    if (levelNum === 1) {
      this.pigs = [
        { x: 920, y: 490, radius: 22, alive: true, hp: 100 },
        { x: 990, y: 490, radius: 22, alive: true, hp: 100 }
      ];
      this.blocks = [
        { x: 890, y: 480, w: 20, h: 80, hp: 100 },
        { x: 950, y: 480, w: 20, h: 80, hp: 100 },
        { x: 920, y: 430, w: 100, h: 20, hp: 100 }
      ];
    } else if (levelNum === 2) {
      this.pigs = [
        { x: 880, y: 490, radius: 22, alive: true, hp: 100 },
        { x: 960, y: 490, radius: 22, alive: true, hp: 100 },
        { x: 920, y: 390, radius: 22, alive: true, hp: 100 }
      ];
      this.blocks = [
        { x: 850, y: 480, w: 20, h: 80, hp: 100 },
        { x: 910, y: 480, w: 20, h: 80, hp: 100 },
        { x: 970, y: 480, w: 20, h: 80, hp: 100 },
        { x: 910, y: 430, w: 140, h: 20, hp: 100 }
      ];
    } else {
      this.pigs = [
        { x: 850, y: 490, radius: 22, alive: true, hp: 100 },
        { x: 930, y: 490, radius: 22, alive: true, hp: 100 },
        { x: 1010, y: 490, radius: 22, alive: true, hp: 100 },
        { x: 930, y: 380, radius: 22, alive: true, hp: 100 }
      ];
      this.blocks = [
        { x: 830, y: 480, w: 20, h: 80, hp: 100 },
        { x: 910, y: 480, w: 20, h: 80, hp: 100 },
        { x: 990, y: 480, w: 20, h: 80, hp: 100 },
        { x: 910, y: 420, w: 180, h: 20, hp: 100 }
      ];
    }
  }

  setupEvents() {
    this.canvas.addEventListener('mousedown', (e) => {
      this.initAudio();
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
      this.initAudio();
      if (!this.visionTracker) {
        this.visionTracker = new VisionTracker((landmarks) => this.handleGestureInput(landmarks));
        const ok = await this.visionTracker.init();
        if (ok) {
          document.getElementById('hud-status').innerText = "Controls: Webcam Active | MediaPipe Tracking";
          document.getElementById('hud-status').style.color = "#2ed573";
        }
      }
    });

    document.getElementById('btn-restart').addEventListener('click', () => this.loadLevel(this.level));
  }

  handleGestureInput(landmarks) {
    const res = this.gestureController.processLandmarks(landmarks);
    if (!res.detected) return;

    const gameX = res.x * this.canvas.width;
    const gameY = res.y * this.canvas.height;

    if (!this.bird.launched) {
      if (res.grabStarted || (res.isGrabbing && !this.bird.grabbing)) {
        const dist = Math.hypot(gameX - this.slingshot.x, gameY - this.slingshot.y);
        if (dist < 130) {
          this.bird.grabbing = true;
          this.playSound(440, 'triangle', 0.1);
        }
      }

      if (this.bird.grabbing) {
        if (res.isGrabbing) {
          const dx = gameX - this.slingshot.x;
          const dy = gameY - this.slingshot.y;
          const pullDist = Math.hypot(dx, dy);
          const maxPull = 130;
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
    this.bird.vx = dx * 0.22;
    this.bird.vy = dy * 0.22;
    this.bird.launched = true;
    this.birdsRemaining--;
    this.playSound(600, 'sine', 0.25);
  }

  spawnHitParticles(x, y, color = '#2ed573') {
    for (let i = 0; i < 15; i++) {
      this.particles.push({
        x: x,
        y: y,
        vx: (Math.random() - 0.5) * 10,
        vy: (Math.random() - 0.5) * 10,
        life: 30,
        color: color
      });
    }
  }

  updatePhysics() {
    // Mouse drag handling when webcam is disabled
    if (this.mouse.isDown && !this.bird.launched && !this.bird.grabbing) {
      const dx = this.mouse.x - this.slingshot.x;
      const dy = this.mouse.y - this.slingshot.y;
      const pullDist = Math.hypot(dx, dy);
      const maxPull = 130;
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
      this.bird.vy += 0.48; // Gravity

      // Ground collision
      if (this.bird.y + this.bird.radius >= 540) {
        this.bird.y = 540 - this.bird.radius;
        this.bird.vx *= 0.6;
        this.bird.vy *= -0.3;

        // Reset bird if stopped
        if (Math.hypot(this.bird.vx, this.bird.vy) < 0.8) {
          if (this.pigs.some(p => p.alive) && this.birdsRemaining > 0) {
            this.bird = { x: 200, y: 460, vx: 0, vy: 0, radius: 20, launched: false, grabbing: false };
          }
        }
      }

      // Pig collision check
      this.pigs.forEach((pig) => {
        if (pig.alive) {
          const dist = Math.hypot(this.bird.x - pig.x, this.bird.y - pig.y);
          if (dist < this.bird.radius + pig.radius) {
            pig.alive = false;
            this.score += 5000;
            this.playSound(800, 'square', 0.2);
            this.spawnHitParticles(pig.x, pig.y, '#2ed573');

            // Level progression check
            if (this.pigs.every(p => !p.alive)) {
              setTimeout(() => {
                const nextLvl = (this.level % 3) + 1;
                this.loadLevel(nextLvl);
              }, 1200);
            }
          }
        }
      });
    }

    // Update collision particles
    this.particles.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;
      p.life--;
    });
    this.particles = this.particles.filter(p => p.life > 0);
  }

  renderTrajectory() {
    if (!this.bird.grabbing && !this.mouse.isDown) return;
    this.ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    const dx = this.slingshot.x - this.bird.x;
    const dy = this.slingshot.y - this.bird.y;
    let simX = this.slingshot.x;
    let simY = this.slingshot.y;
    let simVx = dx * 0.22;
    let simVy = dy * 0.22;

    for (let t = 0; t < 25; t++) {
      simX += simVx;
      simY += simVy;
      simVy += 0.48;
      this.ctx.beginPath();
      this.ctx.arc(simX, simY, 4, 0, 2 * Math.PI);
      this.ctx.fill();
    }
  }

  render() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Background Image
    if (this.assets.background.complete && this.assets.background.naturalWidth !== 0) {
      this.ctx.drawImage(this.assets.background, 0, 0, this.canvas.width, this.canvas.height);
    } else {
      const skyGrad = this.ctx.createLinearGradient(0, 0, 0, 540);
      skyGrad.addColorStop(0, '#70a1ff');
      skyGrad.addColorStop(1, '#eccc68');
      this.ctx.fillStyle = skyGrad;
      this.ctx.fillRect(0, 0, this.canvas.width, 540);
    }

    // Trajectory Projection Line
    if (!this.bird.launched) {
      this.renderTrajectory();
    }

    // Slingshot Rubber Band
    if (!this.bird.launched) {
      this.ctx.strokeStyle = '#301934';
      this.ctx.lineWidth = 7;
      this.ctx.beginPath();
      this.ctx.moveTo(185, 450);
      this.ctx.lineTo(this.bird.x, this.bird.y);
      this.ctx.lineTo(215, 450);
      this.ctx.stroke();
    }

    // Slingshot Sprite
    if (this.assets.sling.complete && this.assets.sling.naturalWidth !== 0) {
      this.ctx.drawImage(this.assets.sling, 175, 430, 55, 120);
    } else {
      this.ctx.fillStyle = '#8B4513';
      this.ctx.fillRect(193, 440, 14, 100);
    }

    // Wood / Column Structure Blocks
    this.blocks.forEach(b => {
      if (this.assets.wood.complete && this.assets.wood.naturalWidth !== 0) {
        this.ctx.drawImage(this.assets.wood, b.x, b.y, b.w, b.h);
      } else {
        this.ctx.fillStyle = '#d2dae2';
        this.ctx.fillRect(b.x, b.y, b.w, b.h);
        this.ctx.strokeRect(b.x, b.y, b.w, b.h);
      }
    });

    // Target Pigs
    this.pigs.forEach(pig => {
      if (pig.alive) {
        if (this.assets.pig.complete && this.assets.pig.naturalWidth !== 0) {
          this.ctx.drawImage(this.assets.pig, pig.x - pig.radius, pig.y - pig.radius, pig.radius * 2, pig.radius * 2);
        } else {
          this.ctx.fillStyle = '#2ed573';
          this.ctx.beginPath();
          this.ctx.arc(pig.x, pig.y, pig.radius, 0, 2 * Math.PI);
          this.ctx.fill();
        }
      }
    });

    // Red Bird
    if (this.assets.bird.complete && this.assets.bird.naturalWidth !== 0) {
      this.ctx.drawImage(this.assets.bird, this.bird.x - this.bird.radius, this.bird.y - this.bird.radius, this.bird.radius * 2.2, this.bird.radius * 2.2);
    } else {
      this.ctx.fillStyle = '#ff4757';
      this.ctx.beginPath();
      this.ctx.arc(this.bird.x, this.bird.y, this.bird.radius, 0, 2 * Math.PI);
      this.ctx.fill();
    }

    // Particles
    this.particles.forEach(p => {
      this.ctx.fillStyle = p.color;
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, 4, 0, 2 * Math.PI);
      this.ctx.fill();
    });

    // HUD Display
    this.ctx.fillStyle = '#ffffff';
    this.ctx.font = 'bold 24px Segoe UI';
    this.ctx.fillText(`SCORE: ${this.score}`, 30, 45);
    this.ctx.fillText(`LEVEL: ${this.level}`, 30, 80);
    this.ctx.fillText(`BIRDS: ${this.birdsRemaining}`, 30, 115);
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
