import itertools as it
import math
import operator as op
import unittest

import pygamelib

from pygamelib import pygame

BULLET_LIVE_TIME = 1000
FIRE_COOLDOWN = 100
FIRE_VELOCITY = 10
PLAYER_ACCELERATION = 0.5
PLAYER_MAX_ACCELERATION = 10

# SHOTSPREAD_ANGLE: the angle either side of the angle shot in, to make a
#                   shotgun spread of bullets.
SHOTSPREAD_ANGLE = 20

# SHOTSPREAD_STEP: the steps between the shot spread angles.
SHOTSPREAD_STEP = 5

# SHOT_THROW_FACTOR: how much movement affects shots.
SHOT_THROW_FACTOR = 0.05

# STOP: threshold below which a value should just be zero.
STOP = 0.3

DEBUG_PLAYER_ATTRS = ['acceleration', 'velocity', 'position']

ORIGIN = pygame.Vector2()

MOVEKEYS = (
    pygame.K_w,
    pygame.K_d,
    pygame.K_s,
    pygame.K_a,
)

FIREKEYS = (
    pygame.K_UP,
    pygame.K_RIGHT,
    pygame.K_DOWN,
    pygame.K_LEFT,
)

class TestInfiniteMix(unittest.TestCase):

    def setUp(self):
        self.mixinf = Mixinf(-1, +1, -2, +2)

    def test_infinite_mix(self):
        self.assertEqual(self.mixinf(+0), -1)
        self.assertEqual(self.mixinf(+1), +1)
        self.assertEqual(self.mixinf(-1.5), -2)
        self.assertEqual(self.mixinf(+1.5), +2)


class Camera:

    def __init__(self, viewport, focus):
        self.viewport = viewport
        self.focus = focus
        self.position = pygame.Vector2(self.focus.center)
        self.acceleration = pygame.Vector2()
        self.velocity = pygame.Vector2()
        self.acceleration_friction = 0
        self.velocity_friction = 0

    def rect_delta(self):
        return -pygame.Vector2(self.viewport.topleft)

    def update(self):
        zero_vector(self.acceleration, STOP)
        zero_vector(self.velocity, STOP)
        self.velocity += self.acceleration
        self.position += self.velocity
        self.focus.center = self.position
        self.viewport.center = self.position


class Entity(pygame.sprite.Sprite):

    def __init__(self, image, position, time, *groups):
        super().__init__(*groups)
        self.image = image
        self.position = position
        self.rect = self.image.get_rect(center=self.position)
        self.acceleration = pygame.Vector2()
        self.velocity = pygame.Vector2()
        self.acceleration_friction = 0
        self.velocity_friction = 0
        self.time = time

    def update(self, elapsed):
        self.time -= elapsed
        if self.time <= 0:
            self.kill()
        integrate(self, ORIGIN, STOP)
        self.rect.center = self.position


class Autofire:

    def __init__(self, delay):
        self.delay = delay
        self.time = 0

    def __bool__(self):
        return self.time == 0

    def fire(self):
        self.time = self.delay

    def update(self, elapsed):
        if self.time > 0:
            if self.time - elapsed < 0:
                self.time = 0
            else:
                self.time -= elapsed


class Shotgun:

    def __init__(self, spread, step, image, fire_velocity):
        self.spread = spread
        self.step = step
        self.image = image
        self.fire_velocity = fire_velocity

    def shoot(self, group, center_velocity, impart_velocity, origin, live_time):
        for angle in shot_angles(center_velocity, self.spread, self.step):
            bullet = Entity(self.image, origin, live_time, group)
            update_scale_angle(bullet.velocity, angle, self.fire_velocity)
            bullet.velocity += impart_velocity


class Mixinf:

    def __init__(self, a, b, below, above):
        self.a = a
        self.b = b
        self.below = below
        self.above = above

    def __call__(self, time):
        if 0 <= time <= 1:
            return self.a * (1 - time) + self.b * time
        elif time < 0:
            return self.below
        elif time > 1:
            return self.above


def crosslines(rect):
    x, y, w, h = rect
    cx = x + w // 2
    cy = y + h // 2
    yield ((x, cy), (x + w, cy))
    yield ((cx, y), (cx, y + h))

def keyed_vector(pressed, magnitude):
    up, right, down, left = map(bool, pressed)
    return (-magnitude * left + magnitude * right, -magnitude * up + magnitude * down)

def rangef(start, stop, step):
    while start < stop:
        yield start
        start += step

def shot_angles(center_velocity, spread, step):
    center_angle = math.atan2(center_velocity.y, center_velocity.x)
    angle = center_angle - math.radians(spread)
    stop = center_angle + math.radians(spread)
    step = math.radians(step)
    yield from rangef(angle, stop, step)

def zero(value, threshold):
    if abs(value) < threshold:
        return 0
    return value

def zero_vector(vector, threshold):
    if abs(vector.x) < threshold:
        vector.x = zero(vector.x, threshold)
    if abs(vector.y) < threshold:
        vector.y = zero(vector.y, threshold)

def update_friction(vector, friction):
    vector.move_towards_ip((0,0), vector.magnitude() * friction)

def integrate(obj, origin, stop_threshold):
    # brake acceleration
    obj.acceleration.move_towards_ip(
        origin,
        obj.acceleration.magnitude() * obj.acceleration_friction
    )
    if obj.velocity.magnitude():
        obj.velocity.clamp_magnitude_ip(PLAYER_MAX_ACCELERATION)
    obj.velocity.move_towards_ip(
        origin,
        obj.velocity.magnitude() * obj.velocity_friction
    )
    zero_vector(obj.velocity, stop_threshold)
    obj.velocity += obj.acceleration
    obj.position += obj.velocity

def cossin(angle):
    yield math.cos(angle)
    yield math.sin(angle)

def scale_by_angle(angle, magnitude):
    for value in cossin(angle):
        yield value * magnitude

def update_scale_angle(vector, angle, magnitude):
    vector.update(*(scale_by_angle(angle, magnitude)))

def blits_with_camera(sprites, camera):
    dx, dy = camera.rect_delta()
    for sprite in sprites:
        yield (sprite.image, sprite.rect.move(dx, dy))

def coordinates(rect):
    x, y, w, h = rect
    r = w + x
    b = h + y
    return (x, y, r, b)

def blit_text_lines(surf, font, color, texts, antialias=True):
    images = [font.render(text, antialias, color) for text in texts]
    rects = [image.get_rect() for image in images]
    for r1, r2 in it.pairwise(rects):
        r2.top = r1.bottom
    surf.blits(zip(images, rects))

def run(display_size, framerate):
    get_movekeys = op.itemgetter(*MOVEKEYS)
    get_firekeys = op.itemgetter(*FIREKEYS)

    pygame.font.init()
    font = pygame.font.SysFont('monospace', 20)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(display_size)
    window = screen.get_rect()
    camera = Camera(window.copy(), window.inflate((-400,)*2))

    entities = pygame.sprite.Group()

    bullet_image = pygame.Surface((16,)*2, pygame.SRCALPHA)
    pygame.draw.circle(bullet_image, 'red', (8,)*2, 8)

    player_image = pygame.Surface((32,)*2)
    player_image.fill('magenta')

    player = Entity(player_image, window.center, math.inf, entities)
    player.acceleration_friction = 0.05
    player.velocity_friction = 0.90
    player.autofire = Autofire(FIRE_COOLDOWN)
    player.gun = Shotgun(SHOTSPREAD_ANGLE, SHOTSPREAD_STEP, bullet_image, FIRE_VELOCITY)

    paused = False
    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif event.key == pygame.K_p:
                    paused = not paused
        if not paused:
            keys = pygame.key.get_pressed()
            movekeys = get_movekeys(keys)
            player.acceleration += keyed_vector(movekeys, PLAYER_ACCELERATION)
            zero_vector(player.acceleration, STOP)
            player.autofire.update(elapsed)
            if player.autofire:
                fire_keys = get_firekeys(keys)
                if any(fire_keys):
                    player.autofire.fire()
                    center_velocity = (
                        keyed_vector(fire_keys, FIRE_VELOCITY)
                        + player.velocity
                        * SHOT_THROW_FACTOR
                    )
                    player.gun.shoot(
                        entities,
                        center_velocity,
                        player.velocity,
                        player.rect.center,
                        BULLET_LIVE_TIME,
                    )
            entities.update(elapsed)
            if camera.focus.contains(player.rect):
                update_friction(camera.acceleration, 0.1)
                update_friction(camera.velocity, 0.5)
            else:
                x1, y1 = camera.focus.center
                x2, y2 = player.rect.center
                angle = math.atan2(y2 - y1, x2 - x1)
                camera.acceleration.x = math.cos(angle)
                camera.acceleration.y = math.sin(angle)
            camera.update()
        screen.fill('black')
        screen.blits(blits_with_camera(entities, camera))
        crossbox = pygame.Rect(0, 0, 30, 30)
        crossbox.center = window.center
        blit_text_lines(
            screen,
            font,
            'white',
            texts = [
                'WASD to move - Arrow keys to shoot',
                f'{clock.get_fps()=:.2f}',
                f'{camera.focus.center=}',
                f'{player.rect.center=}',
                f'{crossbox=}',
            ]
        )
        for start, end in crosslines(crossbox):
            pygame.draw.line(screen, 'white', start, end)
        pygame.display.flip()

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args.display_size, args.framerate)

if __name__ == '__main__':
    main()

# 2024-02-22 Thu.
# Prompted to make a little demo of "Binding of Isaac" style shot throwing.
# https://www.reddit.com/r/pygame/comments/1awi7zu/pygame_problem_projectiles_not_firing_towards/
# 2024-02-26 Mon.
# Draft: posts-mortem
# I like how few classes there are. Feels like a good optimimum of their
# usefulness.
# Text is still frustrating. It takes an awful lot to get print-like output.
