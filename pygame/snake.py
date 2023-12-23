import argparse
import contextlib
import itertools as it
import operator as op
import os

from collections import deque
from itertools import pairwise
from operator import itemgetter

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

from pygame import Rect
from pygame import Vector2

SEGMENT_DIAMETER = 32

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
            self.move()

    def grow(self, n=1):
        """
        Add tail segment
        """
        tail, next_tail = next(pairwise(self.body))
        dir_ = next_tail - tail
        v = tail - dir_ * self.segment_diameter
        self.body.appendleft(v)
        self.colors.appendleft(next(self.color_generator))

    def move(self):
        """
        Slither
        """
        for s1, s2 in pairwise(self.body):
            s1 += s2 - s1
        self.body[-1] += self.head_velocity * self.segment_diameter

        self.head_velocity.update(
            tuple(map(op.mul, self.head_velocity, self.velocity_entropy))
        )


def pressed_key(pressed, key1, key2):
    a = pressed[key1]
    b = pressed[key2]
    if a ^ b:
        if a:
            return key1
        else:
            return key2

def range_spread(origin, dist, step=1):
    return range(origin - dist, origin + dist, step)

def clamp(x, a, b):
    if x < a:
        return a
    elif x > b:
        return b
    return x

def clamp_vector_ip(v, rect):
    v.x = clamp(v.x, rect.left, rect.right)
    v.y = clamp(v.y, rect.top, rect.bottom)

def modulo_vector_ip(v, rect):
    v.x %= rect.width
    v.y %= rect.height

def mix(a, b, x):
    # numerically stable, less floating point errors
    return a * (1 - x) + b * x

def remap(a, b, c, d, x):
    return x*(d-c)/(b-a) + c-a*(d-c)/(b-a)

def run():
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 60

    # head at end of list
    xs = range_spread(
        window.centerx,
        15 * SEGMENT_DIAMETER,
        SEGMENT_DIAMETER,
    )
    ys = it.repeat(window.centery // 4)
    snake_body = deque(map(Vector2, xs, ys))

    snake_colors_cycle = it.cycle(['brown1'] + ['antiquewhite3'] * 3 * 4)
    snake_colors = deque((next(snake_colors_cycle) for _ in snake_body))

    snake = Snake(
        body = snake_body,
        head_velocity = Vector2(0, +1), # down
        colors = snake_colors,
        move_interval = Interval(threshold=100, elapsed=100),
        color_generator = snake_colors_cycle,
        segment_diameter = SEGMENT_DIAMETER,
        velocity_entropy = it.repeat(0.99),
    )

    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

        # update
        pressed = pygame.key.get_pressed()
        snake.update(elapsed, pressed)
        # wrap movement around window
        for point in snake.body:
            modulo_vector_ip(point, window)

        # draw
        screen.fill('black')
        for point, color in zip(snake.body, snake.colors):
            pygame.draw.circle(screen, color, point, snake.segment_radius)
        pygame.display.flip()

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
