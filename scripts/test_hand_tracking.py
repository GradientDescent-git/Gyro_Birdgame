import cv2

from app.vision.hand_tracker import HandTracker


def main():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError(
            "Could not open webcam. "
            "Check camera permissions or try another camera index."
        )

    tracker = HandTracker()

    try:

        while True:

            success, frame = camera.read()

            if not success:
                break

            frame = cv2.flip(frame, 1)

            frame, hand_state = tracker.process(frame)

            if hand_state.detected:

                status = (
                    "PINCH"
                    if hand_state.is_pinching
                    else "OPEN"
                )

                cv2.putText(
                    frame,
                    f"Gesture: {status}",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Pinch distance: {hand_state.pinch_distance:.3f}",
                    (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )

            else:

                cv2.putText(
                    frame,
                    "No hand detected",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("VisionBird - Hand Tracking", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    finally:

        tracker.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()