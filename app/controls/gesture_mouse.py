from __future__ import annotations

import pygame


class GestureMouse:
    """
    Converts normalized hand coordinates into Pygame coordinates.

    Pinch:
        MOUSEBUTTONDOWN

    Release:
        MOUSEBUTTONUP
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
    ) -> None:

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.is_grabbing = False

        self.x = screen_width // 2
        self.y = screen_height // 2

    def update(
        self,
        index_tip: tuple[float, float] | None,
        is_pinching: bool,
    ) -> None:

        if index_tip is None:

            # If the hand disappears while grabbing,
            # release the mouse safely.
            if self.is_grabbing:

                pygame.event.post(
                    pygame.event.Event(
                        pygame.MOUSEBUTTONUP,
                        {
                            "button": 1,
                            "pos": (self.x, self.y),
                        },
                    )
                )

                self.is_grabbing = False

            return

        x_norm, y_norm = index_tip

        # The camera is already mirrored in GestureBridge,
        # so DO NOT mirror X again here.
        x = int(x_norm * self.screen_width)
        y = int(y_norm * self.screen_height)

        # Keep coordinates inside the game window.
        x = max(
            0,
            min(
                self.screen_width - 1,
                x,
            ),
        )

        y = max(
            0,
            min(
                self.screen_height - 1,
                y,
            ),
        )

        self.x = x
        self.y = y

        pygame.mouse.set_pos(
            (x, y)
        )

        # Start grab.
        if is_pinching and not self.is_grabbing:

            pygame.event.post(
                pygame.event.Event(
                    pygame.MOUSEBUTTONDOWN,
                    {
                        "button": 1,
                        "pos": (x, y),
                    },
                )
            )

            self.is_grabbing = True

        # Release grab.
        elif not is_pinching and self.is_grabbing:

            pygame.event.post(
                pygame.event.Event(
                    pygame.MOUSEBUTTONUP,
                    {
                        "button": 1,
                        "pos": (x, y),
                    },
                )
            )

            self.is_grabbing = False