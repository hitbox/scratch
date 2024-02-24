import contextlib
import itertools as it
import math
import operator as op
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

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


def shot_velocity(fire_keys):
    fire_up, fire_right, fire_down, fire_left = fire_keys
    center_velocity = pygame.Vector2()
    if fire_up:
        center_velocity.y = -FIRE_VELOCITY
    if fire_right:
        center_velocity.x = +FIRE_VELOCITY
    if fire_down:
        center_velocity.y = +FIRE_VELOCITY
    if fire_left:
        center_velocity.x = -FIRE_VELOCITY
    return center_velocity

def shot_angles(center_velocity):
    center_angle = math.atan2(center_velocity.y, center_velocity.x)
    angle = center_angle - math.radians(SHOTSPREAD_ANGLE)
    stop = center_angle + math.radians(SHOTSPREAD_ANGLE)
    step = math.radians(SHOTSPREAD_STEP)
    while angle < stop:
        yield angle
        angle += step

def zero(value, threshold):
    if abs(value) < threshold:
        return 0
    return value

def zero_vector(vector, threshold):
    if abs(vector.x) < threshold:
        vector.x = zero(vector.x, threshold)
    if abs(vector.y) < threshold:
        vector.y = zero(vector.y, threshold)

def integrate(obj, origin, stop_threshold):
    obj.acceleration.move_towards_ip(
        origin,
        obj.acceleration.magnitude() * obj.acceleration_friction
    )
    zero_vector(obj.velocity, stop_threshold)
    obj.velocity.move_towards_ip(
        origin,
        obj.velocity.magnitude() * obj.velocity_friction
    )
    obj.velocity += obj.acceleration
    if obj.velocity.magnitude():
        obj.velocity.clamp_magnitude_ip(PLAYER_MAX_ACCELERATION)
    obj.position += obj.velocity

get_movekeys = op.itemgetter(*MOVEKEYS)
get_firekeys = op.itemgetter(*FIREKEYS)

pygame.font.init()
font = pygame.font.SysFont('monospace', 20)
clock = pygame.time.Clock()
framerate = 60
screen = pygame.display.set_mode((800,)*2)
window = screen.get_rect()
ORIGIN = pygame.Vector2()

entities = pygame.sprite.Group()

player_image = pygame.Surface((32,)*2)
player_image.fill('magenta')
player = Entity(player_image, window.center, math.inf, entities)
player.acceleration_friction = 0.05
player.velocity_friction = 0.90

bullet_image = pygame.Surface((16,)*2, pygame.SRCALPHA)
pygame.draw.circle(bullet_image, 'red', (8,)*2, 8)

fired = 0

running = True
while running:
    elapsed = clock.tick(framerate)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
    keys = pygame.key.get_pressed()
    move_up, move_right, move_down, move_left = get_movekeys(keys)
    if move_up:
        player.acceleration.y -= PLAYER_ACCELERATION
    if move_right:
        player.acceleration.x += PLAYER_ACCELERATION
    if move_down:
        player.acceleration.y += PLAYER_ACCELERATION
    if move_left:
        player.acceleration.x -= PLAYER_ACCELERATION
    zero_vector(player.acceleration, STOP)
    if (fired - elapsed) < 0:
        fired = 0
    else:
        fired -= elapsed
    if not fired:
        fire_keys = get_firekeys(keys)
        if any(fire_keys):
            fired = FIRE_COOLDOWN
            center_velocity = shot_velocity(fire_keys)
            center_velocity += player.velocity * SHOT_THROW_FACTOR
            for angle in shot_angles(center_velocity):
                bullet = Entity(
                    bullet_image,
                    player.rect.center,
                    BULLET_LIVE_TIME,
                    entities,
                )
                bullet.velocity.x = math.cos(angle) * FIRE_VELOCITY
                bullet.velocity.y = math.sin(angle) * FIRE_VELOCITY
                bullet.velocity += player.velocity
    entities.update(elapsed)
    screen.fill('black')
    entities.draw(screen)
    texts = [
        'WASD to move',
        'Arrow keys to shoot',
    ]
    texts.extend(f'{name}={getattr(player, name)}' for name in DEBUG_PLAYER_ATTRS)
    texts.append(f'{fired=}')
    images = [font.render(text, True, 'white') for text in texts]
    rects = [image.get_rect() for image in images]
    for r1, r2 in it.pairwise(rects):
        r2.top = r1.bottom
    screen.blits(zip(images, rects))
    pygame.display.flip()

# 2024-02-22 Thu.
# Prompted to make a little demo of "Binding of Isaac" style shot throwing.
# https://www.reddit.com/r/pygame/comments/1awi7zu/pygame_problem_projectiles_not_firing_towards/
