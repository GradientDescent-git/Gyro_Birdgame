from __future__ import annotations

import math
import os

import pygame
import pymunk as pm
from pymunk import Vec2d


# ============================================================
# PATH CONFIGURATION
# ============================================================

# Absolute path to:
# E:\VisionBird\third_party\angry-birds-python\src
SRC_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# Absolute path to:
# E:\VisionBird\third_party\angry-birds-python\resources
RESOURCES_DIR = os.path.abspath(
    os.path.join(
        SRC_DIR,
        "..",
        "resources",
    )
)


# Absolute path to:
# E:\VisionBird\third_party\angry-birds-python\resources\images
IMAGES_DIR = os.path.join(
    RESOURCES_DIR,
    "images",
)


# ============================================================
# ASSET PATHS
# ============================================================

WOOD_IMAGE_PATH = os.path.join(
    IMAGES_DIR,
    "wood.png",
)


WOOD2_IMAGE_PATH = os.path.join(
    IMAGES_DIR,
    "wood2.png",
)


# ============================================================
# POLYGON
# ============================================================

class Polygon:

    def __init__(
        self,
        pos,
        length,
        height,
        space,
        mass=5.0,
    ):

        # ----------------------------------------------------
        # PHYSICS BODY
        # ----------------------------------------------------

        moment = 1000

        body = pm.Body(
            mass,
            moment,
        )

        body.position = Vec2d(
            *pos
        )


        # ----------------------------------------------------
        # PHYSICS SHAPE
        # ----------------------------------------------------

        shape = pm.Poly.create_box(
            body,
            (
                length,
                height,
            ),
        )

        shape.color = (
            0,
            0,
            255,
        )

        shape.friction = 0.5

        shape.collision_type = 2


        # ----------------------------------------------------
        # ADD TO PHYSICS SPACE
        # ----------------------------------------------------

        space.add(
            body,
            shape,
        )


        # ----------------------------------------------------
        # STORE REFERENCES
        # ----------------------------------------------------

        self.body = body

        self.shape = shape


        # ----------------------------------------------------
        # LOAD WOOD TEXTURES
        #
        # Using absolute paths prevents failures when the game
        # is launched from:
        #
        # E:\VisionBird
        #
        # instead of the original src directory.
        # ----------------------------------------------------

        wood = pygame.image.load(
            WOOD_IMAGE_PATH
        ).convert_alpha()


        wood2 = pygame.image.load(
            WOOD2_IMAGE_PATH
        ).convert_alpha()


        # ----------------------------------------------------
        # BEAM IMAGE
        # ----------------------------------------------------

        beam_rect = pygame.Rect(
            251,
            357,
            86,
            22,
        )


        self.beam_image = wood.subsurface(
            beam_rect
        ).copy()


        # ----------------------------------------------------
        # COLUMN IMAGE
        # ----------------------------------------------------

        column_rect = pygame.Rect(
            16,
            252,
            22,
            84,
        )


        self.column_image = wood2.subsurface(
            column_rect
        ).copy()


    # ========================================================
    # COORDINATE CONVERSION
    # ========================================================

    def to_pygame(
        self,
        p,
    ):
        """
        Convert Pymunk coordinates to Pygame coordinates.
        """

        return (
            int(p.x),
            int(-p.y + 600),
        )


    # ========================================================
    # DRAW POLYGON
    # ========================================================

    def draw_poly(
        self,
        element,
        screen,
    ):
        """
        Draw beams and columns.
        """

        poly = self.shape


        # ----------------------------------------------------
        # GET POLYGON VERTICES
        # ----------------------------------------------------

        vertices = poly.get_vertices()

        vertices.append(
            vertices[0]
        )


        points = map(
            self.to_pygame,
            vertices,
        )


        points = list(
            points
        )


        # ----------------------------------------------------
        # DEBUG OUTLINE
        # ----------------------------------------------------

        color = (
            255,
            0,
            0,
        )


        pygame.draw.lines(
            screen,
            color,
            False,
            points,
        )


        # ====================================================
        # DRAW BEAM
        # ====================================================

        if element == "beams":

            position = poly.body.position


            position = Vec2d(
                *self.to_pygame(
                    position
                )
            )


            angle_degrees = (
                math.degrees(
                    poly.body.angle
                )
                + 180
            )


            rotated_image = pygame.transform.rotate(
                self.beam_image,
                angle_degrees,
            )


            offset = (
                Vec2d(
                    *rotated_image.get_size()
                )
                / 2.0
            )


            position = (
                position
                - offset
            )


            screen.blit(
                rotated_image,
                (
                    position.x,
                    position.y,
                ),
            )


        # ====================================================
        # DRAW COLUMN
        # ====================================================

        elif element == "columns":

            position = poly.body.position


            position = Vec2d(
                *self.to_pygame(
                    position
                )
            )


            angle_degrees = (
                math.degrees(
                    poly.body.angle
                )
                + 180
            )


            rotated_image = pygame.transform.rotate(
                self.column_image,
                angle_degrees,
            )


            offset = (
                Vec2d(
                    *rotated_image.get_size()
                )
                / 2.0
            )


            position = (
                position
                - offset
            )


            screen.blit(
                rotated_image,
                (
                    position.x,
                    position.y,
                ),
            )