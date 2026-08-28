from app.game.gesture_bridge import GestureBridge


def main():
    bridge = GestureBridge(
        screen_width=1200,
        screen_height=650,
        camera_index=0,
    )

    print("VisionBird Gesture Bridge Test Started")
    print("Move your hand in front of the camera.")
    print("Press ESC in the camera window to stop.")

    try:
        while True:
            state = bridge.update()

            print(
                f"\r"
                f"detected={state['detected']} | "
                f"x={state['x']} | "
                f"y={state['y']} | "
                f"pinching={state['pinching']} | "
                f"started={state['pinch_started']} | "
                f"released={state['pinch_released']}   ",
                end="",
                flush=True,
            )

            # ESC in the OpenCV window makes detected False.
            # For this standalone test, stop after the window is closed.
            try:
                import cv2
                if cv2.getWindowProperty(
                    bridge.window_name,
                    cv2.WND_PROP_VISIBLE,
                ) < 1:
                    break
            except cv2.error:
                break

    except KeyboardInterrupt:
        print("\nStopping test...")

    finally:
        bridge.close()
        print("\nGesture bridge closed safely.")


if __name__ == "__main__":
    main()