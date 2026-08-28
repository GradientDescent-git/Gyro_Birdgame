import cv2

from app.vision.hand_tracker import HandTracker


def main():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("Could not open camera.")

        return


    tracker = HandTracker()

    print("Hand tracker started.")
    print("Show your hand clearly to the camera.")
    print("Press Q or ESC to exit.")


    while True:

        success, frame = camera.read()

        if not success:

            print("Could not read frame.")

            break


        # Mirror camera
        frame = cv2.flip(
            frame,
            1,
        )


        frame, hand_state = tracker.process(
            frame
        )


        # ------------------------------------------------
        # STATUS
        # ------------------------------------------------

        if hand_state.detected:

            status = "HAND DETECTED"

            if hand_state.is_pinching:

                gesture = "PINCH / GRAB"

                color = (
                    0,
                    0,
                    255,
                )

            else:

                gesture = "OPEN / RELEASE"

                color = (
                    0,
                    255,
                    0,
                )

        else:

            status = "NO HAND"

            gesture = "SHOW YOUR HAND"

            color = (
                0,
                255,
                255,
            )


        cv2.putText(
            frame,
            status,
            (
                20,
                40,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            color,
            2,
        )


        cv2.putText(
            frame,
            gesture,
            (
                20,
                80,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )


        # Show pinch distance

        if hand_state.detected:

            cv2.putText(
                frame,
                f"Pinch distance: {hand_state.pinch_distance:.3f}",
                (
                    20,
                    120,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (
                    255,
                    255,
                    255,
                ),
                2,
            )


        cv2.imshow(
            "VisionBird Hand Test",
            frame,
        )


        key = cv2.waitKey(1) & 0xFF


        if key == ord("q"):

            break


        if key == 27:

            break


    tracker.close()

    camera.release()

    cv2.destroyAllWindows()

    print("Hand tracker closed.")


if __name__ == "__main__":

    main()