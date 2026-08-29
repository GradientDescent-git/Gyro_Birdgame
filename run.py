#!/usr/bin/env python3
"""
VisionBird — Real-Time Computer Vision Gesture-Controlled Physics Game

Entry point script.
Usage:
    python run.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.game.game_controller import GameController


def main() -> None:
    print("=" * 60)
    print(" VisionBird — Computer Vision Gesture-Controlled Physics Game")
    print("=" * 60)
    print("Starting application...")
    print("Webcam Hand Control:")
    print(" - Move index finger to target")
    print(" - Pinch thumb + index finger to grab bird")
    print(" - Relative pull to aim slingshot")
    print(" - Release pinch to launch bird")
    print(" - Press ESC in webcam window to disable CV and use mouse")
    print("=" * 60)

    controller = GameController(project_root=PROJECT_ROOT)
    controller.run()


if __name__ == "__main__":
    main()
