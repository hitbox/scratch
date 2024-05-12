import argparse
import itertools as it
import math
import os
import random
import string

from collections import deque
from itertools import cycle
from itertools import pairwise
from operator import attrgetter

import pygamelib

from pygamelib import pygame

corner_attrs = ['topleft', 'topright', 'bottomright', 'bottomleft']
side_attrs = ['top', 'right', 'bottom', 'left']

square_points = attrgetter(*(corner_attrs + ['topleft']))
sides = attrgetter(*side_attrs)

exclude = [
    'black',
    'dark',
    'gray',
    'grey',
    'light',
    'medium',
    'pale',
    'white',
]

colorfuls = [
    (name, color)
    for name, color in pygame.color.THECOLORS.items()
    if not any(unwanted in name for unwanted in exclude)
    and not set(name).intersection(string.digits)
]

colorfuls = dict(colorfuls)

def get_rect(rect, **kwargs):
    rect = pygame.Rect(rect).copy()
    for key, val in kwargs.items():
        setattr(rect, key, val)
    return rect

def lerp(a, b, t):
    """
    Return position between a and b at 'time' t
    """
    return a * (1 - t) + b * t

def ilerp(a, b, x):
    return (x - a) / (b - a)

def remap(a, b, c, d, x):
    return lerp(c, d, ilerp(a, b, x))

def lerp_iterable(a, b, t):
    class_ = type(a)
    if class_ is not type(b):
        raise TypeError('a and b must be same type')
    return class_(lerp(i1, i2, t) for i1, i2 in zip(a, b))

def render_lines(font, antialias, color, lines):
    images = [font.render(text, antialias, color) for text in lines]
    rects = [image.get_rect() for image in images]
    for r1, r2 in pairwise(rects):
        r2.top = r1.bottom
    return (images, rects)

def ease_in(t):
    return t * t

def flip(t):
    return 1 - t

def ease_out(t):
    return 1 - math.sqrt(1 - t)

def ease_in_ease_out(t):
    return lerp(ease_in(t), ease_out(t), t)

def avg(iterable):
    return sum(iterable) / len(iterable)

def triangle(x, amplitude, period):
    # triangle wave
    # https://stackoverflow.com/a/22400799/2680592
    # y = (A/P) * (P - abs(x % (2*P) - P) )
    return (amplitude / period) * (period - abs(x % (2*period) - period))

def spiralize(points, n, t):
    for a, b in it.pairwise(points):
        c = lerp_iterable(a, b, t)
        yield c

def run(args):
    pygame.font.init()
    monofont = pygame.font.SysFont('monospace', 18)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((800,)*2)
    frame = screen.get_rect()

    square = frame.inflate((-150,)*2)

    fps_target = 60
    fps = deque(maxlen=1000)
    npoints = 75
    x = 0.0
    x_step = .005
    t_side_min = .005
    t_side_max = .100
    running = True
    while running:
        # tick
        elapsed = clock.tick(fps_target)
        frame_fps = clock.get_fps()
        fps.append(frame_fps)
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        # update
        x += x_step
        time = triangle(x, 1, 1)

        # update
        eased_t = ease_in_ease_out(time)
        side_t = remap(0, 1, t_side_min, t_side_max, eased_t)
        # XXX
        # - this is cleaner but broken now
        # - feel like there is a problem between a square and lerps inside the
        #   square which produces spirals which are not squares
        points = list(spiralize(square_points(square), npoints, side_t))

        # draw
        screen.fill('black')
        for line, color in zip(pairwise(points), cycle(colorfuls)):
            p1, p2 = line
            pygame.draw.line(screen, color, p1, p2, 1)

        # debugging
        texts = [
            f'{x=:0.3f}',
            f'{eased_t=:.3f}',
            f'{side_t=:.3f}',
            f'{frame_fps=:.3f}',
            f'{avg(fps)=:.2f}',
            f'{min(fps)=:.2f}',
            f'{max(fps)=:.2f}',
        ]
        images, rects = render_lines(monofont, True, 'white', texts)
        pygamelib.move_as_one(rects, bottomright=frame.bottomright)
        for image, rect in zip(images, rects):
            screen.blit(image, rect)

        pygame.display.flip()

def main(argv=None):
    # https://twitter.com/Rainmaker1973/status/1625113235320934400
    parser = argparse.ArgumentParser(
        description = main.__doc__,
    )
    args = parser.parse_args(argv)
    run(args)

if __name__ == '__main__':
    main()
