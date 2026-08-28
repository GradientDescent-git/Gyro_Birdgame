import cv2

from app.controls.gesture_controller import GestureController
from app.vision.hand_tracker import HandTracker


def main() -> None:

    tracker = HandTracker()

    controller = GestureController(
        smoothing=0.25,
    )

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError(
            "Could not open webcam."
        )

    print("Gesture controller started.")
    print("PINCH -> grabbing")
    print("OPEN after PINCH -> release")
    print("Press Q to quit.")

    try:

        while True:

            success, frame = camera.read()

            if not success:
                break

            frame = cv2.flip(frame, 1)

            frame, hand_state = tracker.process(frame)

            control_state = controller.update(
                hand_state
            )

            status = (
                f"Hand: {control_state.hand_detected} | "
                f"Grab: {control_state.is_grabbing} | "
                f"Release: {control_state.release_triggered}"
            )

            position = (
                f"Aim: "
                f"({control_state.aim_x:.3f}, "
                f"{control_state.aim_y:.3f})"
            )

            cv2.putText(
                frame,
                status,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                position,
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            if control_state.is_grabbing:

                cv2.putText(
                    frame,
                    "GRABBING",
                    (20, 115),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 255),
                    3,
                )

            elif control_state.release_triggered:

                cv2.putText(
                    frame,
                    "RELEASE!",
                    (20, 115),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    3,
                )

            else:

                cv2.putText(
                    frame,
                    "OPEN",
                    (20, 115),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (255, 255, 0),
                    3,
                )

            cv2.imshow(
                "VisionBird - Gesture Controller",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    finally:

        camera.release()
        tracker.close()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()