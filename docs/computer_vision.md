# VisionBird — Computer Vision Pipeline

## Pipeline Pipeline Stages

1. **Frame Capture**: Reads 640x480 resolution frame from OpenCV `cv2.VideoCapture`.
2. **Preprocessing**: Converts frame from BGR to RGB and mirrors horizontally (`cv2.flip(frame, 1)`).
3. **Landmark Detection**: MediaPipe Palm Detection & Hand Landmark Model predicts 21 3D points.
4. **Feature Extraction**:
   - `Hand Scale` ($S$): Euclidean distance between Wrist (Landmark 0) and Middle Finger MCP (Landmark 9):
     $$S = \sqrt{(x_9 - x_0)^2 + (y_9 - y_0)^2}$$
   - `Raw Pinch Distance` ($d_{raw}$): Distance between Index Tip (8) and Thumb Tip (4):
     $$d_{raw} = \sqrt{(x_8 - x_4)^2 + (y_8 - y_4)^2}$$
   - `Normalized Pinch Distance` ($d_{norm}$):
     $$d_{norm} = \frac{d_{raw}}{S}$$
5. **Pinch Recognition & Hysteresis**:
   - Pinch Start: Triggered when $d_{norm} < 0.06$.
   - Pinch Release: Triggered when $d_{norm} > 0.09$.
6. **Filtering**: Exponential low-pass filter:
   $$x_{smoothed} = \alpha \cdot x_{raw} + (1 - \alpha) \cdot x_{prev}$$
   where $\alpha = 0.85$.
