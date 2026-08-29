# VisionBird — Deployment Guide

VisionBird supports two deployment targets:

## 1. Desktop Reference Implementation (Python / OpenCV / MediaPipe / Pygame)

### Requirements
- Python 3.10+
- Webcam

### Quick Start
```bash
# Clone repository
git clone https://github.com/GradientDescent-git/Gyro_Birdgame.git
cd Gyro_Birdgame

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch application
python run.py
```

## 2. Browser Deployment (GitHub Pages Static Hosting)

The browser version in `web/` is fully static and client-side:

- Host the root `web/` directory on GitHub Pages, Vercel, Netlify, or any HTTP server.
- HTTPS is required for webcam permissions (`navigator.mediaDevices.getUserMedia`).
