import argparse
import contextlib
import math
import os
import random
import string

from collections import deque
from itertools import cycle
from itertools import pairwise
from operator import attrgetter

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

from pygame import Vector2 as Vector

corner_attrs = ['topleft', 'topright', 'bottomright', 'bottomleft']
side_attrs = ['top', 'right', 'bottom', 'left']

corners = attrgetter(*corner_attrs)
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

def wrap(rects):
    tops, rights, bottoms, lefts = zip(*map(sides, rects))
    top = min(tops)
    right = max(rights)
    bottom = max(bottoms)
    left = min(lefts)
    width = right - left
    height = bottom - top
    return pygame.Rect(left, top, width, height)

def get_rect(rect, **kwargs):
    rect = rect.copy()
    for key, val in kwargs.items():
        setattr(rect, key, val)
    return rect

def lerp(a, b, t):
    "Return position between a and b at 'time' t"
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

def move(rects, **kwargs):
    wrapped = wrap(rects)
    moved = get_rect(wrapped, **kwargs)
    dx = moved.x - wrapped.x
    dy = moved.y - wrapped.y
    for rect in rects:
        rect.x += dx
        rect.y += dy

def spiralize_builtin(points, n, t):
    if len(points) < 5:
        raise ValueError('points must be at least five points')
    i = 1
    while len(points) < n:
        a, b = points[i:i+2]
        c = Vector(a).lerp(b, t)
        i += 1

def spiralize_custom(points, n, t):
    if len(points) < 5:
        raise ValueError('points must be at least five points')
    i = 1
    while len(points) < n:
        a, b = points[i:i+2]
        c = lerp_iterable(a, b, t)
        points.append(c)
        i += 1

spiralize = spiralize_custom
#spiralize = spiralize_builtin

def ease_in(t):
    return t * t

def flip(t):
    return 1 - t

def ease_out(t):
    return 1 - math.sqrt(1 - t)
    return flip(math.sqrt(flip(t)))

def ease_in_ease_out(t):
    return lerp(ease_in(t), ease_out(t), t)

def avg(iterable):
    return sum(iterable) / len(iterable)

def triangle(x, amplitude, period):
    # triangle wave
    # https://stackoverflow.com/a/22400799/2680592
    # y = (A/P) * (P - abs(x % (2*P) - P) )
    return (amplitude / period) * (period - abs(x % (2*period) - period))

def run(args):
    ""
    pygame.font.init()
    monofont = pygame.font.SysFont('monospace', 18)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((800,)*2)
    frame = screen.get_rect()

    square = frame.inflate((-150,)*2)

    # TODO
    # - values plotted over time?
    fps_target = 60
    fps = deque(maxlen=1000)
    npoints = 75
    x = 0.0
    x_step = .005
    t_side_min = .005
    t_side_max = .100
    is_recording = bool(args.output)
    frame_number = 0
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
        points = list(square_points(square))
        eased_t = ease_in_ease_out(time)
        side_t = remap(0, 1, t_side_min, t_side_max, eased_t)
        spiralize(points, npoints, side_t)

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
        ]
        if args.fps:
            texts.extend([
                f'{frame_fps=:.3f}',
                f'{avg(fps)=:.2f}',
                f'{min(fps)=:.2f}',
                f'{max(fps)=:.2f}',
            ])
        images, rects = render_lines(monofont, True, 'white', texts)
        move(rects, bottomright=frame.bottomright)
        for image, rect in zip(images, rects):
            screen.blit(image, rect)

        pygame.display.flip()
        # recording
        if is_recording:
            filename = args.output.format(frame_number)
            if os.path.exists(filename):
                raise ValueError('output filename exists')
            pygame.image.save(screen, filename)
            frame_number += 1

def main(argv=None):
    ""
    # https://twitter.com/Rainmaker1973/status/1625113235320934400
    parser = argparse.ArgumentParser(
        description = main.__doc__,
    )
    parser.add_argument(
        '--output',
        help = 'Format string for frame output.',
    )
    parser.add_argument(
        '--once',
        action = 'store_true',
    )
    parser.add_argument(
        '--fps',
        action = 'store_true',
    )
    args = parser.parse_args(argv)
    run(args)

if __name__ == '__main__':
    main()
