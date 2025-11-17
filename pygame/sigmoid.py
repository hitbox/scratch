import argparse
import contextlib
import itertools as it
import math
import operator
import os

from collections import deque
from functools import partial
from types import SimpleNamespace

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class sizetype:

    def __init__(self, separator=',', type=int, duplicate_size=2):
        self.separator = separator
        self.type = type
        self.duplicate_size = duplicate_size

    def __call__(self, string):
        size = tuple(map(int, string.replace(',', ' ').split()))
        while len(size) < self.duplicate_size:
            size += size
        return size


class StepAttr:

    def __init__(self, obj, name, step):
        self.obj = obj
        self.name = name
        self.step = step

    def __call__(self):
        new = getattr(self.obj, self.name) + self.step
        setattr(self.obj, self.name, new)
        return new


class KeyMatch:

    def __init__(self, keycode, modifiers):
        self.keycode = keycode
        self.modifiers = modifiers

    def __hash__(self):
        return id(self)


class Sigmoid:

    def __init__(self, center=0.5, k=10):
        self.center = center
        self.k = k

    def formula(self):
        return f'sigmoid(center={self.center:.2f}, k={self.k})'

    def __str__(self):
        return self.formula()

    def __call__(self, t):
        return 1 / (1 + math.exp(-self.k * (t - self.center)))


class Timer:

    def __init__(self, duration, easing=None):
        self.duration = duration
        self.time = 0
        self.easing = easing

    def restart(self):
        self.time = 0

    def update(self, elapsed):
        if self.time < self.duration:
            self.time += elapsed
        else:
            self.time = self.duration

    def lerp(self):
        p = self.time / self.duration
        if self.easing:
            p = self.easing(p)
        return p


class Circle:

    def __init__(self, color, radius, fill):
        self.color = color
        self.radius = radius
        self.fill = fill

    def draw(self, surf, position):
        pygame.draw.circle(surf, self.color, position, self.radius, self.fill)


class Move:

    def __init__(self, start, end, timer):
        self.start = start
        self.end = end
        self.timer = timer

    def update(self, elapsed):
        if hasattr(self.timer, 'update'):
            self.timer.update(elapsed)


def draw_graph(surf, function):
    rect = surf.get_rect()
    for screen_x in range(rect.left, rect.right):
        norm_x = map_scalar(rect.left, rect.right, 0, 1, screen_x)
        y = function(norm_x)
        screen_y = int(map_scalar(0, 1, rect.bottom - 1, rect.top, y))
        surf.set_at((screen_x, screen_y), 'red')

def lerp_scalar(a, b, t):
    return a + (b - a) * t

def lerp_containers(a, b, t):
    class_ = type(a)
    return class_(lerp_scalar(aa, bb, t) for aa, bb in zip(a, b))

def map_scalar(a, b, c, d, x):
    t = (x - a) / (b - a)
    return c + (d - c) * t

def render_lines(font, lines, color, antialias=True):
    for line in lines:
        yield font.render(line, antialias, color)

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--size',
        default = '400,400',
        type = sizetype(),
        help = 'Screen size. Default: %(default)s',
    )
    parser.add_argument(
        '--scale',
        default = 2,
        type = int,
        help = 'Screen size. Default: %(default)s',
    )
    parser.add_argument(
        '--start',
        default = 'midright',
        help = 'Start position',
    )
    parser.add_argument(
        '--end',
        default = 'midleft',
        help = 'End position',
    )
    parser.add_argument(
        '--duration',
        default = 1000,
        type = int,
        help = 'Animation duration in integer milliseconds.',
    )
    parser.add_argument(
        '-k',
        type = int,
        help = 'Sigmoid k value.',
    )
    parser.add_argument(
        '-c', '--center',
        default = 0.5,
        type = float,
        help = 'Sigmoid center value.',
    )
    return parser

def main():
    parser = argument_parser()
    args = parser.parse_args()

    screen = pygame.display.set_mode(args.size)
    frame = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 60

    pygame.font.init()

    font = pygame.font.SysFont(None, 24)

    graph_rect = frame.inflate((-frame.width / 2, -frame.height / 2))
    graph_surf = pygame.Surface(graph_rect.size)
    surf_rect = graph_surf.get_rect()

    kwargs = {}
    if args.k is not None:
        kwargs['k'] = args.k
    if args.center is not None:
        kwargs['center'] = args.center
    easing = Sigmoid(**kwargs)
    draw_graph(graph_surf, easing)

    timer = Timer(args.duration, easing=easing)
    start = getattr(frame, args.start)
    end = getattr(frame, args.end)
    animation = Move(start, end, Timer(args.duration))
    circle = Circle('red', radius=10, fill=0)

    steppers = {
        pygame.K_UP: StepAttr(easing, 'center', 0.05),
        pygame.K_DOWN: StepAttr(easing, 'center', -0.05),
        pygame.K_LEFT: StepAttr(easing, 'k', 1),
        pygame.K_RIGHT: StepAttr(easing, 'k', -1),
        pygame.K_d: StepAttr(timer, 'duration', -1),
        (pygame.K_d, pygame.KMOD_SHIFT): StepAttr(timer, 'duration', 1),
    }

    running = True
    elapsed = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif event.key == pygame.K_r:
                    timer.restart()

        pressed = pygame.key.get_pressed()
        mods = pygame.key.get_mods()
        for key, stepper in steppers.items():
            try:
                key, modifiers = key
            except TypeError:
                modifiers = pygame.KMOD_NONE
            if pressed[key] and modifiers & mods:
                stepper()
                timer.restart()
                graph_surf.fill('black')
                draw_graph(graph_surf, easing)

        timer.update(elapsed)
        t = timer.lerp()
        screen.fill('black')

        # Draw sigmoid graph and point
        screen.blit(graph_surf, graph_surf.get_rect(center=frame.center))
        # x from time t in normal to rect horizontal
        x = int(map_scalar(0, 1, graph_rect.left, graph_rect.right, t))
        sig_y = easing(t)
        y = int(map_scalar(0, 1, graph_rect.bottom - 1, graph_rect.top, sig_y))
        pygame.draw.circle(screen, 'red', (x, y), 5)

        point = lerp_containers(animation.start, animation.end, t)
        circle.draw(screen, point)

        lines = [
            'r: restart',
            f'{easing.formula()=}',
            f'{timer.time=}',
            f'{timer.duration=}',
            f'{t=:.2f}',
            f'{elapsed=}',
        ]
        images = list(render_lines(font, lines, 'white'))
        rects = []
        for image in images:
            if rects:
                rect = image.get_rect(topleft=rects[-1].bottomleft)
            else:
                rect = image.get_rect()
            rects.append(rect)

        for image, rect in zip(images, rects):
            screen.blit(image, rect)

        pygame.display.update()
        elapsed = clock.tick(framerate)

if __name__ == '__main__':
    main()
