# VisionBird Roadmap & Known Limitations

## Known Limitations & Failure Modes

1. **Low-Light Environments**:
   - *Behavior*: MediaPipe hand landmark detection confidence drops under 0.4 in low ambient light.
   - *Mitigation*: Fallback mode automatically preserves cursor position and enables mouse control seamlessly.

2. **Occlusion & Gloves**:
   - *Behavior*: Wearing dark gloves or heavy hand occlusion can degrade finger tip detection.
   - *Mitigation*: Posture calibration and hysteresis thresholding prevent unexpected state triggers.

3. **Multiple Hands in Frame**:
   - *Behavior*: MediaPipe is constrained to `max_num_hands=1` to minimize latency. If multiple hands enter the camera frame, tracking prioritizes the primary detected palm.

## Future Roadmap

- [ ] **WebGPU Acceleration**: Integrate `@mediapipe/tasks-vision` WebGPU backend for ultra-low 60 FPS browser inference.
- [ ] **Dynamic Pinch Calibration**: Machine-learning based adaptive pinch baseline per user hand size.
- [ ] **Multi-Hand Cooperative Gameplay**: Support two-player local gesture slingshot battles.
