from __future__ import annotations

import math
import os
import sys
import time

import pygame
import pymunk as pm


# ============================================================
# PATH SETUP
# ============================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

GAME_ROOT = os.path.abspath(
    os.path.join(
        CURRENT_DIR,
        "..",
    )
)

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        CURRENT_DIR,
        "..",
        "..",
        "..",
    )
)

RESOURCES_DIR = os.path.join(
    GAME_ROOT,
    "resources",
)

IMAGES_DIR = os.path.join(
    RESOURCES_DIR,
    "images",
)

SOUNDS_DIR = os.path.join(
    RESOURCES_DIR,
    "sounds",
)


# ============================================================
# IMPORT PATHS
# ============================================================

if CURRENT_DIR not in sys.path:

    sys.path.insert(
        0,
        CURRENT_DIR,
    )

if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT,
    )


from characters import Bird
from level import Level

from app.game.gesture_bridge import GestureBridge

from app.config.gesture_settings import (
    GESTURE_SENSITIVITY,
    GESTURE_SMOOTHING,
    HAND_LOST_TIMEOUT,
    MAX_FORWARD_PULL,
    MAX_PULL_DISTANCE,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def image_path(filename: str) -> str:

    return os.path.join(
        IMAGES_DIR,
        filename,
    )


def sound_path(filename: str) -> str:

    return os.path.join(
        SOUNDS_DIR,
        filename,
    )


# ============================================================
# PYGAME SETUP
# ============================================================

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 650

screen = pygame.display.set_mode(
    (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
    )
)

pygame.display.set_caption(
    "VisionBird"
)

clock = pygame.time.Clock()

running = True


# ============================================================
# LOAD ASSETS
# ============================================================

redbird = pygame.image.load(
    image_path(
        "red-bird3.png"
    )
).convert_alpha()

background2 = pygame.image.load(
    image_path(
        "background3.png"
    )
).convert_alpha()

sling_image = pygame.image.load(
    image_path(
        "sling-3.png"
    )
).convert_alpha()

full_sprite = pygame.image.load(
    image_path(
        "full-sprite.png"
    )
).convert_alpha()

buttons = pygame.image.load(
    image_path(
        "selected-buttons.png"
    )
).convert_alpha()

pig_happy = pygame.image.load(
    image_path(
        "pig_failed.png"
    )
).convert_alpha()

stars = pygame.image.load(
    image_path(
        "stars-edited.png"
    )
).convert_alpha()


# ============================================================
# PIG IMAGE
# ============================================================

rect = pygame.Rect(
    181,
    1050,
    50,
    50,
)

cropped = full_sprite.subsurface(
    rect
).copy()

pig_image = pygame.transform.scale(
    cropped,
    (
        30,
        30,
    ),
)


# ============================================================
# STARS
# ============================================================

rect = pygame.Rect(
    0,
    0,
    200,
    200,
)

star1 = stars.subsurface(
    rect
).copy()


rect = pygame.Rect(
    204,
    0,
    200,
    200,
)

star2 = stars.subsurface(
    rect
).copy()


rect = pygame.Rect(
    426,
    0,
    200,
    200,
)

star3 = stars.subsurface(
    rect
).copy()


# ============================================================
# BUTTONS
# ============================================================

rect = pygame.Rect(
    164,
    10,
    60,
    60,
)

pause_button = buttons.subsurface(
    rect
).copy()


rect = pygame.Rect(
    24,
    4,
    100,
    100,
)

replay_button = buttons.subsurface(
    rect
).copy()


rect = pygame.Rect(
    142,
    365,
    130,
    100,
)

next_button = buttons.subsurface(
    rect
).copy()


rect = pygame.Rect(
    18,
    212,
    100,
    100,
)

play_button = buttons.subsurface(
    rect
).copy()


# ============================================================
# SLINGSHOT POSITION
# ============================================================

sling_x = 135
sling_y = 450

sling2_x = 160
sling2_y = 450


# ============================================================
# PHYSICS
# ============================================================

space = pm.Space()

space.gravity = (
    0.0,
    -700.0,
)

pigs = []
birds = []
balls = []
polys = []
beams = []
columns = []
poly_points = []

ball_number = 0

polys_dict = {}


# ============================================================
# GAME VARIABLES
# ============================================================

mouse_distance = 0

rope_lenght = 90

angle = 0

x_mouse = sling_x
y_mouse = sling_y

mouse_pressed = False

t1 = 0
t2 = 0


# ============================================================
# GESTURE CONTROL SETTINGS
# ============================================================

gesture_detected = False

gesture_grabbed = False

gesture_x = sling_x
gesture_y = sling_y

last_hand_seen = 0.0


# ------------------------------------------------------------
# RELATIVE GRAB STATE
# ------------------------------------------------------------

gesture_grab_start_x = sling_x
gesture_grab_start_y = sling_y

gesture_pull_start_x = sling_x
gesture_pull_start_y = sling_y


# ------------------------------------------------------------
# SMOOTH GESTURE PULL
# ------------------------------------------------------------

gesture_smooth_x = float(
    sling_x
)

gesture_smooth_y = float(
    sling_y
)


# ============================================================
# COLORS
# ============================================================

RED = (
    255,
    0,
    0,
)

BLUE = (
    0,
    0,
    255,
)

BLACK = (
    0,
    0,
    0,
)

WHITE = (
    255,
    255,
    255,
)

GREEN = (
    0,
    255,
    0,
)


# ============================================================
# GAME STATE
# ============================================================

score = 0

game_state = 0

bird_path = []

counter = 0

restart_counter = False

bonus_score_once = True

wall = False


# ============================================================
# FONTS
# ============================================================

bold_font = pygame.font.SysFont(
    "arial",
    30,
    bold=True,
)

bold_font2 = pygame.font.SysFont(
    "arial",
    40,
    bold=True,
)

bold_font3 = pygame.font.SysFont(
    "arial",
    50,
    bold=True,
)


# ============================================================
# STATIC FLOOR
# ============================================================

static_body = pm.Body(
    body_type=pm.Body.STATIC
)

static_lines = [

    pm.Segment(
        static_body,
        (
            0.0,
            60.0,
        ),
        (
            1200.0,
            60.0,
        ),
        0.0,
    )

]

static_lines1 = [

    pm.Segment(
        static_body,
        (
            1200.0,
            60.0,
        ),
        (
            1200.0,
            800.0,
        ),
        0.0,
    )

]

for line in static_lines:

    line.elasticity = 0.95
    line.friction = 1
    line.collision_type = 3


for line in static_lines1:

    line.elasticity = 0.95
    line.friction = 1
    line.collision_type = 3


space.add(
    static_body
)

for line in static_lines:

    space.add(
        line
    )


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def to_pygame(p):

    return (
        int(p.x),
        int(-p.y + 600),
    )


def vector(
    p0,
    p1,
):

    a = p1[0] - p0[0]

    b = p1[1] - p0[1]

    return (
        a,
        b,
    )


def unit_vector(v):

    h = (
        (
            v[0] ** 2
        )
        +
        (
            v[1] ** 2
        )
    ) ** 0.5

    if h == 0:

        h = 0.000000000000001

    ua = v[0] / h
    ub = v[1] / h

    return (
        ua,
        ub,
    )


def distance(
    xo,
    yo,
    x,
    y,
):

    dx = x - xo
    dy = y - yo

    return (
        (
            dx ** 2
            +
            dy ** 2
        )
    ) ** 0.5


# ============================================================
# LIMIT GESTURE PULL
# ============================================================

def limit_pull_position(
    target_x,
    target_y,
):

    target_x = min(
        target_x,
        sling_x + MAX_FORWARD_PULL,
    )

    dx = target_x - sling_x
    dy = target_y - sling_y

    pull_distance = math.sqrt(
        dx * dx
        +
        dy * dy
    )

    if pull_distance > MAX_PULL_DISTANCE:

        scale = (
            MAX_PULL_DISTANCE
            /
            pull_distance
        )

        target_x = sling_x + dx * scale
        target_y = sling_y + dy * scale

    return (
        target_x,
        target_y,
    )


# ============================================================
# UPDATE RELATIVE GESTURE PULL
# ============================================================

def update_gesture_pull():

    global x_mouse
    global y_mouse

    global gesture_smooth_x
    global gesture_smooth_y

    hand_dx = (
        gesture_x
        -
        gesture_grab_start_x
    )

    hand_dy = (
        gesture_y
        -
        gesture_grab_start_y
    )

    target_x = (
        gesture_pull_start_x
        +
        hand_dx * GESTURE_SENSITIVITY
    )

    target_y = (
        gesture_pull_start_y
        +
        hand_dy * GESTURE_SENSITIVITY
    )

    target_x, target_y = limit_pull_position(
        target_x,
        target_y,
    )

    gesture_smooth_x += (
        target_x
        -
        gesture_smooth_x
    ) * GESTURE_SMOOTHING

    gesture_smooth_y += (
        target_y
        -
        gesture_smooth_y
    ) * GESTURE_SMOOTHING

    x_mouse = int(
        gesture_smooth_x
    )

    y_mouse = int(
        gesture_smooth_y
    )


# ============================================================
# MUSIC
# ============================================================

def load_music():

    song = sound_path(
        "angry-birds.ogg"
    )

    pygame.mixer.music.load(
        song
    )

    pygame.mixer.music.play(
        -1
    )


# ============================================================
# SLINGSHOT ACTION
# ============================================================

def sling_action():

    global mouse_distance
    global angle

    v = vector(
        (
            sling_x,
            sling_y,
        ),
        (
            x_mouse,
            y_mouse,
        ),
    )

    uv = unit_vector(
        v
    )

    uv1 = uv[0]
    uv2 = uv[1]

    mouse_distance = distance(
        sling_x,
        sling_y,
        x_mouse,
        y_mouse,
    )

    pu = (
        uv1 * rope_lenght + sling_x,
        uv2 * rope_lenght + sling_y,
    )

    bigger_rope = 102

    x_redbird = x_mouse - 20
    y_redbird = y_mouse - 20

    if mouse_distance > rope_lenght:

        pux, puy = pu

        pux -= 20
        puy -= 20

        screen.blit(
            redbird,
            (
                pux,
                puy,
            ),
        )

        pu2 = (
            uv1 * bigger_rope + sling_x,
            uv2 * bigger_rope + sling_y,
        )

        pygame.draw.line(
            screen,
            BLACK,
            (
                sling2_x,
                sling2_y,
            ),
            pu2,
            5,
        )

        pygame.draw.line(
            screen,
            BLACK,
            (
                sling_x,
                sling_y,
            ),
            pu2,
            5,
        )

    else:

        mouse_distance += 10

        pu3 = (
            uv1 * mouse_distance + sling_x,
            uv2 * mouse_distance + sling_y,
        )

        pygame.draw.line(
            screen,
            BLACK,
            (
                sling2_x,
                sling2_y,
            ),
            pu3,
            5,
        )

        screen.blit(
            redbird,
            (
                x_redbird,
                y_redbird,
            ),
        )

        pygame.draw.line(
            screen,
            BLACK,
            (
                sling_x,
                sling_y,
            ),
            pu3,
            5,
        )

    dy = y_mouse - sling_y
    dx = x_mouse - sling_x

    if dx == 0:

        dx = 0.00000000000001

    angle = math.atan(
        float(dy) / dx
    )


# ============================================================
# LAUNCH BIRD
# ============================================================

def launch_bird():

    global mouse_pressed
    global gesture_grabbed
    global t1
    global t2
    global mouse_distance

    if not mouse_pressed:

        return

    if level.number_of_birds <= 0:

        mouse_pressed = False
        gesture_grabbed = False

        return

    mouse_pressed = False
    gesture_grabbed = False

    level.number_of_birds -= 1

    t1 = time.time() * 1000

    xo = 154
    yo = 156

    launch_distance = min(
        mouse_distance,
        rope_lenght,
    )

    if x_mouse < sling_x + 5:

        bird = Bird(
            launch_distance,
            angle,
            xo,
            yo,
            space,
        )

    else:

        bird = Bird(
            -launch_distance,
            angle,
            xo,
            yo,
            space,
        )

    birds.append(
        bird
    )

    print(
        "BIRD LAUNCHED!"
    )

    if level.number_of_birds == 0:

        t2 = time.time()


# ============================================================
# LEVEL CLEARED
# ============================================================

def draw_level_cleared():

    global game_state
    global bonus_score_once
    global score

    level_cleared = bold_font3.render(
        "Level Cleared!",
        True,
        WHITE,
    )

    if (
        level.number_of_birds >= 0
        and len(pigs) == 0
    ):

        if bonus_score_once:

            score += (
                level.number_of_birds - 1
            ) * 10000

            bonus_score_once = False

        game_state = 4

        rect = pygame.Rect(
            300,
            0,
            600,
            800,
        )

        pygame.draw.rect(
            screen,
            BLACK,
            rect,
        )

        screen.blit(
            level_cleared,
            (
                450,
                90,
            ),
        )

        if (
            score >= level.one_star
            and score <= level.two_star
        ):

            screen.blit(
                star1,
                (
                    310,
                    190,
                ),
            )

        elif (
            score >= level.two_star
            and score <= level.three_star
        ):

            screen.blit(
                star1,
                (
                    310,
                    190,
                ),
            )

            screen.blit(
                star2,
                (
                    500,
                    170,
                ),
            )

        elif score >= level.three_star:

            screen.blit(
                star1,
                (
                    310,
                    190,
                ),
            )

            screen.blit(
                star2,
                (
                    500,
                    170,
                ),
            )

            screen.blit(
                star3,
                (
                    700,
                    200,
                ),
            )

        score_level_cleared = bold_font2.render(
            str(score),
            True,
            WHITE,
        )

        screen.blit(
            score_level_cleared,
            (
                550,
                400,
            ),
        )

        screen.blit(
            replay_button,
            (
                510,
                480,
            ),
        )

        screen.blit(
            next_button,
            (
                620,
                480,
            ),
        )


# ============================================================
# LEVEL FAILED
# ============================================================

def draw_level_failed():

    global game_state

    failed = bold_font3.render(
        "Level Failed",
        True,
        WHITE,
    )

    if (
        level.number_of_birds <= 0
        and time.time() - t2 > 5
        and len(pigs) > 0
    ):

        game_state = 3

        rect = pygame.Rect(
            300,
            0,
            600,
            800,
        )

        pygame.draw.rect(
            screen,
            BLACK,
            rect,
        )

        screen.blit(
            failed,
            (
                450,
                90,
            ),
        )

        screen.blit(
            pig_happy,
            (
                380,
                120,
            ),
        )

        screen.blit(
            replay_button,
            (
                520,
                460,
            ),
        )


# ============================================================
# RESTART
# ============================================================

def restart():

    global mouse_pressed
    global gesture_grabbed
    global gesture_x
    global gesture_y
    global gesture_grab_start_x
    global gesture_grab_start_y
    global gesture_pull_start_x
    global gesture_pull_start_y
    global x_mouse
    global y_mouse
    global gesture_smooth_x
    global gesture_smooth_y

    mouse_pressed = False

    gesture_grabbed = False

    gesture_x = sling_x
    gesture_y = sling_y

    gesture_grab_start_x = sling_x
    gesture_grab_start_y = sling_y

    gesture_pull_start_x = sling_x
    gesture_pull_start_y = sling_y

    x_mouse = sling_x
    y_mouse = sling_y

    gesture_smooth_x = float(
        sling_x
    )

    gesture_smooth_y = float(
        sling_y
    )

    for pig in pigs[:]:

        space.remove(
            pig.shape,
            pig.shape.body,
        )

        pigs.remove(
            pig
        )

    for bird in birds[:]:

        space.remove(
            bird.shape,
            bird.shape.body,
        )

        birds.remove(
            bird
        )

    for column in columns[:]:

        space.remove(
            column.shape,
            column.shape.body,
        )

        columns.remove(
            column
        )

    for beam in beams[:]:

        space.remove(
            beam.shape,
            beam.shape.body,
        )

        beams.remove(
            beam
        )


# ============================================================
# COLLISION HANDLERS
# ============================================================

def post_solve_bird_pig(
    arbiter,
    space,
    data,
):

    global score

    a, b = arbiter.shapes

    pigs_to_remove = []

    for pig in pigs:

        if (
            a == pig.shape
            or b == pig.shape
        ):

            pigs_to_remove.append(
                pig
            )

            score += 10000

    for pig in pigs_to_remove:

        if pig in pigs:

            space.remove(
                pig.shape,
                pig.shape.body,
            )

            pigs.remove(
                pig
            )


def post_solve_bird_wood(
    arbiter,
    space,
    data,
):

    global score

    if arbiter.total_impulse.length <= 1100:

        return

    a, b = arbiter.shapes

    poly_to_remove = []

    for column in columns:

        if (
            a == column.shape
            or b == column.shape
        ):

            poly_to_remove.append(
                column
            )

    for beam in beams:

        if (
            a == beam.shape
            or b == beam.shape
        ):

            poly_to_remove.append(
                beam
            )

    for poly in poly_to_remove:

        if poly in columns:

            columns.remove(
                poly
            )

        if poly in beams:

            beams.remove(
                poly
            )

        space.remove(
            poly.shape,
            poly.shape.body,
        )

        score += 5000


def post_solve_pig_wood(
    arbiter,
    space,
    data,
):

    global score

    if arbiter.total_impulse.length <= 700:

        return

    a, b = arbiter.shapes

    pigs_to_remove = []

    for pig in pigs:

        if (
            a == pig.shape
            or b == pig.shape
        ):

            pig.life -= 20

            if pig.life <= 0:

                pigs_to_remove.append(
                    pig
                )

                score += 10000

    for pig in pigs_to_remove:

        if pig in pigs:

            space.remove(
                pig.shape,
                pig.shape.body,
            )

            pigs.remove(
                pig
            )


# ============================================================
# COLLISION REGISTRATION
# ============================================================

space.add_collision_handler(
    0,
    1,
).post_solve = post_solve_bird_pig

space.add_collision_handler(
    0,
    2,
).post_solve = post_solve_bird_wood

space.add_collision_handler(
    1,
    2,
).post_solve = post_solve_pig_wood


# ============================================================
# GESTURE BRIDGE
# ============================================================

gesture_bridge = None

try:

    gesture_bridge = GestureBridge(
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
    )

    print()
    print("========================================")
    print(" VisionBird Gesture Control Enabled")
    print("========================================")
    print()
    print("HOW TO PLAY:")
    print()
    print("1. Move your hand comfortably in front")
    print("   of the camera.")
    print()
    print("2. Move your index finger near the bird.")
    print()
    print("3. Pinch thumb + index to grab.")
    print()
    print("4. Keep pinching and move your hand")
    print("   LEFT / UP / DOWN to pull.")
    print()
    print("5. Release the pinch to launch.")
    print()
    print("Mouse control also works.")
    print("ESC -> Exit")
    print("========================================")
    print()

except Exception as error:

    print()
    print(
        f"WARNING: Gesture control unavailable: {error}"
    )

    print(
        "Continuing with normal mouse control."
    )

    print()

    gesture_bridge = None


# ============================================================
# LOAD GAME
# ============================================================

load_music()

level = Level(
    pigs,
    columns,
    beams,
    space,
)

level.number = 0

level.load_level()


# ============================================================
# MAIN GAME LOOP
# ============================================================

while running:

    # ========================================================
    # GESTURE UPDATE
    # ========================================================

    gesture_detected = False

    if gesture_bridge is not None:

        try:

            hand_state = gesture_bridge.update()

            gesture_detected = bool(
                hand_state.get(
                    "detected",
                    False,
                )
            )

            current_pinching = bool(
                hand_state.get(
                    "pinching",
                    False,
                )
            )

            pinch_started = bool(
                hand_state.get(
                    "pinch_started",
                    False,
                )
            )

            pinch_released = bool(
                hand_state.get(
                    "pinch_released",
                    False,
                )
            )

            # ====================================================
            # HAND DETECTED
            # ====================================================

            if gesture_detected:

                gesture_x = int(
                    hand_state.get(
                        "x",
                        gesture_x,
                    )
                )

                gesture_y = int(
                    hand_state.get(
                        "y",
                        gesture_y,
                    )
                )

                gesture_x = max(
                    0,
                    min(
                        SCREEN_WIDTH - 1,
                        gesture_x,
                    ),
                )

                gesture_y = max(
                    0,
                    min(
                        SCREEN_HEIGHT - 1,
                        gesture_y,
                    ),
                )

                last_hand_seen = time.time()

                # =================================================
                # PINCH START = TRY TO GRAB
                # =================================================

                if (
                    (pinch_started or current_pinching)
                    and not gesture_grabbed
                    and level.number_of_birds > 0
                    and game_state == 0
                ):
                    gesture_grabbed = True
                    mouse_pressed = True

                    gesture_grab_start_x = gesture_x
                    gesture_grab_start_y = gesture_y

                    gesture_pull_start_x = sling_x
                    gesture_pull_start_y = sling_y

                    gesture_smooth_x = float(sling_x)
                    gesture_smooth_y = float(sling_y)

                    x_mouse = sling_x
                    y_mouse = sling_y

                    print("GESTURE: BIRD GRABBED")

                # =================================================
                # PINCH HOLD = PULL
                # =================================================

                if (
                    gesture_grabbed
                    and current_pinching
                    and game_state == 0
                ):
                    mouse_pressed = True
                    x_mouse = gesture_x
                    y_mouse = gesture_y

                # =================================================
                # PINCH RELEASE = LAUNCH
                # =================================================

                if (
                    gesture_grabbed
                    and pinch_released
                    and game_state == 0
                ):

                    print(
                        "GESTURE: BIRD RELEASED"
                    )

                    launch_bird()

            # ====================================================
            # HAND LOST
            # ====================================================

            else:

                if (
                    gesture_grabbed
                    and (
                        time.time()
                        - last_hand_seen
                        > HAND_LOST_TIMEOUT
                    )
                ):

                    print(
                        "GESTURE: HAND LOST - GRAB CANCELLED"
                    )

                    gesture_grabbed = False

                    mouse_pressed = False

                    x_mouse = sling_x
                    y_mouse = sling_y

                    gesture_smooth_x = float(
                        sling_x
                    )

                    gesture_smooth_y = float(
                        sling_y
                    )

        except Exception as error:

            print(
                f"Gesture tracking warning: {error}"
            )

            gesture_detected = False


    # ========================================================
    # EVENT PROCESSING
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        elif (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):

            running = False


        elif (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_w
        ):

            if wall:

                for line in static_lines1:

                    if line in space.shapes:

                        space.remove(
                            line
                        )

                wall = False

            else:

                for line in static_lines1:

                    if line not in space.shapes:

                        space.add(
                            line
                        )

                wall = True


        elif (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_s
        ):

            space.gravity = (
                0.0,
                -10.0,
            )

            level.bool_space = True


        elif (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_n
        ):

            space.gravity = (
                0.0,
                -700.0,
            )

            level.bool_space = False


        # ====================================================
        # MOUSE PRESS
        # ====================================================

        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            x_mouse, y_mouse = event.pos

            if (
                60 < x_mouse < 270
                and 340 < y_mouse < 570
                and level.number_of_birds > 0
                and game_state == 0
                and not gesture_grabbed
            ):

                mouse_pressed = True


        # ====================================================
        # MOUSE RELEASE
        # ====================================================

        elif (
            event.type == pygame.MOUSEBUTTONUP
            and event.button == 1
        ):

            x_mouse, y_mouse = event.pos

            if (
                mouse_pressed
                and not gesture_grabbed
                and game_state == 0
            ):

                launch_bird()


            # PAUSE BUTTON

            if (
                x_mouse < 100
                and 70 < y_mouse < 180
            ):

                game_state = 1


            # PAUSE MENU

            if game_state == 1:

                if (
                    500 < x_mouse < 650
                    and 180 < y_mouse < 310
                ):

                    game_state = 0


                elif (
                    500 < x_mouse < 650
                    and 300 < y_mouse < 430
                ):

                    restart()

                    level.load_level()

                    game_state = 0

                    bird_path = []

                    score = 0

                    bonus_score_once = True


            # FAILED SCREEN

            if game_state == 3:

                if (
                    480 < x_mouse < 650
                    and 430 < y_mouse < 600
                ):

                    restart()

                    level.load_level()

                    game_state = 0

                    bird_path = []

                    score = 0

                    bonus_score_once = True


            # LEVEL CLEARED

            if game_state == 4:

                if (
                    x_mouse > 610
                    and y_mouse > 450
                ):

                    restart()

                    level.number += 1

                    game_state = 0

                    level.load_level()

                    score = 0

                    bird_path = []

                    bonus_score_once = True


                elif (
                    500 < x_mouse < 610
                    and y_mouse > 450
                ):

                    restart()

                    level.load_level()

                    game_state = 0

                    bird_path = []

                    score = 0

                    bonus_score_once = True


    # ========================================================
    # MOUSE POSITION
    # ========================================================

    if (
        not gesture_detected
        and not gesture_grabbed
    ):

        x_mouse, y_mouse = pygame.mouse.get_pos()


    # ========================================================
    # DRAW BACKGROUND
    # ========================================================

    screen.fill(
        (
            130,
            200,
            100,
        )
    )

    screen.blit(
        background2,
        (
            0,
            -50,
        ),
    )


    # ========================================================
    # FIRST SLINGSHOT
    # ========================================================

    rect = pygame.Rect(
        50,
        0,
        70,
        220,
    )

    screen.blit(
        sling_image,
        (
            138,
            420,
        ),
        rect,
    )


    # ========================================================
    # BIRD TRAJECTORY
    # ========================================================

    for point in bird_path:

        pygame.draw.circle(
            screen,
            WHITE,
            point,
            5,
        )


    # ========================================================
    # WAITING BIRDS
    # ========================================================

    if level.number_of_birds > 0:

        for i in range(
            level.number_of_birds - 1
        ):

            x = 100 - (
                i * 35
            )

            screen.blit(
                redbird,
                (
                    x,
                    508,
                ),
            )


    # ========================================================
    # SLINGSHOT
    # ========================================================

    if (
        mouse_pressed
        and level.number_of_birds > 0
        and game_state == 0
    ):

        sling_action()

    else:

        if (
            time.time() * 1000 - t1 > 300
            and level.number_of_birds > 0
        ):

            screen.blit(
                redbird,
                (
                    130,
                    426,
                ),
            )

        else:

            pygame.draw.line(
                screen,
                BLACK,
                (
                    sling_x,
                    sling_y - 8,
                ),
                (
                    sling2_x,
                    sling2_y - 7,
                ),
                5,
            )


    # ========================================================
    # BIRDS
    # ========================================================

    birds_to_remove = []

    counter += 1

    for bird in birds:

        if bird.shape.body.position.y < 0:

            birds_to_remove.append(
                bird
            )

        p = to_pygame(
            bird.shape.body.position
        )

        x, y = p

        x -= 22
        y -= 20

        screen.blit(
            redbird,
            (
                x,
                y,
            ),
        )

        pygame.draw.circle(
            screen,
            BLUE,
            p,
            int(
                bird.shape.radius
            ),
            2,
        )

        if (
            counter >= 3
            and time.time() - t1 < 5
        ):

            bird_path.append(
                p
            )

            restart_counter = True


    if restart_counter:

        counter = 0

        restart_counter = False


    for bird in birds_to_remove:

        if bird in birds:

            space.remove(
                bird.shape,
                bird.shape.body,
            )

            birds.remove(
                bird
            )


    # ========================================================
    # STATIC FLOOR
    # ========================================================

    for line in static_lines:

        body = line.body

        pv1 = (
            body.position
            + line.a.rotated(
                body.angle
            )
        )

        pv2 = (
            body.position
            + line.b.rotated(
                body.angle
            )
        )

        p1 = to_pygame(
            pv1
        )

        p2 = to_pygame(
            pv2
        )

        pygame.draw.lines(
            screen,
            (
                150,
                150,
                150,
            ),
            False,
            [
                p1,
                p2,
            ],
        )


    # ========================================================
    # DRAW PIGS
    # ========================================================

    pigs_to_remove = []

    for pig_object in pigs:

        pig = pig_object.shape

        if pig.body.position.y < 0:

            pigs_to_remove.append(
                pig_object
            )

        p = to_pygame(
            pig.body.position
        )

        x, y = p

        angle_degrees = math.degrees(
            pig.body.angle
        )

        img = pygame.transform.rotate(
            pig_image,
            angle_degrees,
        )

        w, h = img.get_size()

        x -= w * 0.5
        y -= h * 0.5

        screen.blit(
            img,
            (
                x,
                y,
            ),
        )


    for pig_object in pigs_to_remove:

        if pig_object in pigs:

            space.remove(
                pig_object.shape,
                pig_object.shape.body,
            )

            pigs.remove(
                pig_object
            )


    # ========================================================
    # DRAW STRUCTURES
    # ========================================================

    for column in columns:

        column.draw_poly(
            "columns",
            screen,
        )


    for beam in beams:

        beam.draw_poly(
            "beams",
            screen,
        )


    # ========================================================
    # PHYSICS
    # ========================================================

    if game_state == 0:

        dt = 1.0 / 100.0

        for _ in range(2):

            space.step(
                dt
            )


    # ========================================================
    # SECOND SLINGSHOT
    # ========================================================

    rect = pygame.Rect(
        0,
        0,
        60,
        200,
    )

    screen.blit(
        sling_image,
        (
            120,
            420,
        ),
        rect,
    )


    # ========================================================
    # SCORE
    # ========================================================

    score_font = bold_font.render(
        "SCORE",
        True,
        WHITE,
    )

    number_font = bold_font.render(
        str(score),
        True,
        WHITE,
    )

    screen.blit(
        score_font,
        (
            1060,
            90,
        ),
    )

    screen.blit(
        number_font,
        (
            1060,
            130,
        ),
    )


    # ========================================================
    # PAUSE BUTTON
    # ========================================================

    screen.blit(
        pause_button,
        (
            10,
            90,
        ),
    )


    # ========================================================
    # PAUSE MENU
    # ========================================================

    if game_state == 1:

        screen.blit(
            play_button,
            (
                500,
                200,
            ),
        )

        screen.blit(
            replay_button,
            (
                500,
                300,
            ),
        )


    # ========================================================
    # GAME OVERLAYS
    # ========================================================

    draw_level_cleared()

    draw_level_failed()


    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()

    clock.tick(
        50
    )

    pygame.display.set_caption(
        "VisionBird | FPS: "
        + str(
            round(
                clock.get_fps(),
                1,
            )
        )
    )


# ============================================================
# CLEANUP
# ============================================================

if gesture_bridge is not None:

    try:

        gesture_bridge.close()

    except Exception as error:

        print(
            f"Gesture cleanup warning: {error}"
        )


pygame.quit()

print(
    "VisionBird closed cleanly."
)