import argparse
import itertools as it
import operator as op

from collections import deque
from itertools import pairwise
from operator import itemgetter

from pygamelib import pygame

from pygame import Rect
from pygame import Vector2

SEGMENT_DIAMETER = 32

class Engine:

    def __init__(self):
        self.running = False

    def run(self, state):
        state.start(engine=self)
        self.running = True
        while self.running:
            state.update(engine=self)


class Interval:

    def __init__(self, threshold, elapsed=0):
        self.threshold = threshold
        self.elapsed = elapsed
        self.activated = False

    def update(self, elapsed):
        new_elapsed = self.elapsed + elapsed
        if new_elapsed < self.threshold:
            self.elapsed = new_elapsed
            self.activated = False
        else:
            # achieved threshold
            self.activated = True
            self.elapsed = new_elapsed % self.threshold


class Snake:

    def __init__(
        self,
        body,
        head_velocity,
        colors,
        move_interval,
        color_generator,
        segment_diameter,
        velocity_entropy,
        move_delta = 0.03,
        max_velocity = 1.25,
    ):
        self.body = body
        self.head_velocity = head_velocity
        self.colors = colors
        self.move_interval = move_interval
        self.color_generator = color_generator
        self.segment_diameter = segment_diameter
        self.segment_radius = segment_diameter // 2
        self.velocity_entropy = velocity_entropy
        self.move_count = 0
        self.grow_moves = 10
        self.move_delta = move_delta
        self.max_velocity = max_velocity
        self.get_movekeys = itemgetter(
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_DOWN,
        )

    def update(self, elapsed, pressed):
        k_left, k_right, k_up, k_down = self.get_movekeys(pressed)
        if k_left:
            self.head_velocity.x -= self.move_delta
        if k_right:
            self.head_velocity.x += self.move_delta
        if k_up:
            self.head_velocity.y -= self.move_delta
        if k_down:
            self.head_velocity.y += self.move_delta
        self.head_velocity.clamp_magnitude_ip(self.max_velocity)

        self.move_interval.update(elapsed)
        if self.move_interval.activated:
            self.move_count += 1
            # grow every n moves
            if self.move_count % self.grow_moves == 0:
                self.grow()
            self.move(elapsed)

    def grow(self, n=1):
        """
        Add tail segment
        """
        tail, next_tail = next(pairwise(self.body))
        dir_ = next_tail - tail
        v = tail - dir_ * self.segment_diameter
        self.body.appendleft(v)
        self.colors.appendleft(next(self.color_generator))

    def move(self, elapsed):
        """
        Slither
        """
        ms = elapsed / 1000
        for s1, s2 in pairwise(self.body):
            s1 += (s2 - s1) * ms
        self.body[-1] += self.head_velocity * ms

        # entropy head velocity
        self.head_velocity.update(
            tuple(map(op.mul, self.head_velocity, self.velocity_entropy))
        )

    def points_colors(self):
        return zip(self.body, self.colors)


class SnakeState:

    def __init__(self, snake):
        self.snake = snake
        self.update_snake_images()

    def update_snake_images(self):
        self.snake_images = {}
        for color in set(self.snake.colors):
            image = pygame.Surface((self.snake.segment_diameter,)*2, pygame.SRCALPHA)
            rect = image.get_rect()
            pygame.draw.circle(image, color, rect.center, self.snake.segment_radius)
            self.snake_images[color] = image

    def start(self, engine):
        self.screen = pygame.display.set_mode((800,)*2)
        self.window = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.framerate = 60
        self.elapsed = None
        self.pressed = None

    def update(self, engine):
        self.elapsed = self.clock.tick(self.framerate)
        self.events(engine)
        self.pressed = pygame.key.get_pressed()
        self.update_snake(engine)
        self.draw(engine)

    def update_snake(self, engine):
        self.snake.update(self.elapsed, self.pressed)
        # wrap movement around window
        for point in self.snake.body:
            modulo_vector_ip(point, self.window)

    def draw(self, engine):
        self.screen.fill('black')
        for point, color in self.snake.points_colors():
            image = self.snake_images[color]
            self.screen.blit(image, image.get_rect(center=point))
        pygame.display.flip()

    def events(self, engine):
        for event in pygame.event.get():
            method = getattr(self, event_methodname(event), None)
            if method is not None:
                method(engine, event)

    def do_quit(self, engine, event):
        engine.running = False

    def do_keydown(self, engine, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.event.post(pygame.event.Event(pygame.QUIT))


def pressed_key(pressed, key1, key2):
    a = pressed[key1]
    b = pressed[key2]
    if a ^ b:
        if a:
            return key1
        else:
            return key2

def event_methodname(event, prefix='do_'):
    name = pygame.event.event_name(event.type).lower()
    return f'{prefix}{name}'

def range_spread(origin, dist, step=1):
    return range(origin - dist, origin + dist, step)

def clamp(x, a, b):
    if x < a:
        return a
    elif x > b:
        return b
    return x

def modulo_vector_ip(v, rect):
    v.x %= rect.width
    v.y %= rect.height

def mix(a, b, x):
    # numerically stable, less floating point errors
    return a * (1 - x) + b * x

def remap(a, b, c, d, x):
    return x*(d-c)/(b-a) + c-a*(d-c)/(b-a)

def run():
    # head at end of list
    xs = range_spread(
        0,
        15 * SEGMENT_DIAMETER,
        SEGMENT_DIAMETER,
    )
    ys = it.repeat(0)
    snake_body = deque(map(Vector2, xs, ys))

    snake_colors_cycle = it.cycle(['brown1'] + ['antiquewhite3'] * 3 * 4)
    snake_colors = deque((next(snake_colors_cycle) for _ in snake_body))

    snake = Snake(
        body = snake_body,
        head_velocity = Vector2(0, +500), # down
        colors = snake_colors,
        move_interval = Interval(threshold=100, elapsed=100),
        color_generator = snake_colors_cycle,
        segment_diameter = SEGMENT_DIAMETER,
        velocity_entropy = it.repeat(0.99),
        move_delta = 1,
        max_velocity = 500,
    )

    state = SnakeState(snake)
    engine = Engine()
    engine.run(state)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()

# 2023-12-22
# - https://www.reddit.com/r/pygame/comments/18oi4xt/snake_game_in_python_and_pygame_source_code_is_in/
# - https://github.com/DataWizual/Snake-game-in-python-and-Pygame/tree/main
# - was inspired by the calculation of the orientation/direction of the
#   segments by vector math
# - dungeon crawler snake?
