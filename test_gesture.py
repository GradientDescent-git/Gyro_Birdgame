from __future__ import annotations

import cv2
import pygame

from app.game.gesture_bridge import GestureBridge


def main():

    # Initialize Pygame because GestureMouse
    # uses pygame.mouse.set_pos()
    pygame.init()

    # Create a tiny hidden/test window so
    # the pygame mouse system is initialized.
    pygame.display.set_mode(
        (
            1,
            1,
        )
    )

    bridge = None

    try:

        bridge = GestureBridge(
            screen_width=1200,
            screen_height=650,
        )

        print("GestureBridge started.")
        print("Press Q or ESC to close.")

        while True:

            hand_state = bridge.update()

            if hand_state is not None:

                print(
                    "Detected:",
                    hand_state.detected,
                    "| Pinching:",
                    hand_state.is_pinching,
                )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q") or key == 27:

                break

    finally:

        if bridge is not None:

            bridge.close()

        pygame.quit()

        print("Gesture test closed.")


if __name__ == "__main__":

    main()