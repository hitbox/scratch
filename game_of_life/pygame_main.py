import argparse
import contextlib
import itertools as it
import math
import operator as op
import os

from types import SimpleNamespace

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

import patterns

from game_of_life import evolve_generator

class Style:

    def __init__(
        self,
        foreground = 'white',
        background = 'black',
        border_color = None,
        margin = 0,
        padding = 0,
    ):
        self.foreground = foreground
        self.background = background
        self.border_color = border_color
        self.margin = margin
        self.padding = padding


def namedcolor(name, **kwargs):
    color = pygame.Color(name)
    for key, val in kwargs.items():
        setattr(color, key, val)
    return color

def copyrect(rect, **kwargs):
    rect = rect.copy()
    for key, val in kwargs.items():
        setattr(rect, key, val)
    return rect

def wraprects(rects):
    return pygame.Rect((0,)*4).unionall(rects)

def gen_align_as(rects, **kwargs):
    original = wraprects(rects)
    positioned = copyrect(original, **kwargs)
    delta = pygame.Vector2(positioned.topleft) - original.topleft
    for rect in rects:
        rect.topleft += delta
        yield rect

def align_as(rects, **kwargs):
    container = type(rects)
    return container(gen_align_as(rects, **kwargs))

def render_lines(font, lines, color, antialias=True):
    for line in lines:
        yield font.render(line, antialias, color)

def run(pattern, cell_size=None, step_speed=None):
    pygame.font.init()
    screen = pygame.display.set_mode((500,)*2)
    frame = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 60
    font = pygame.font.SysFont('monospace', 20)

    styles = SimpleNamespace(
        cells = Style('lightyellow1'),
        grid = Style('darkorange'),
        text = Style(
            'lightyellow1',
            namedcolor('black', a=190),
            border_color = 'lightyellow1',
        ),
    )

    states = evolve_generator(pattern)
    if step_speed is None:
        step_speed = math.inf

    if cell_size is None:
        cell_size = (40,)*2
    cell = pygame.Rect((0, 0), cell_size)

    cellsrect = pygame.Rect((0,)*4)
    gridlines = set()
    frame_number = 0
    time = math.inf
    running = True
    while running:
        elapsed = clock.tick(framerate)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif event.key == pygame.K_r:
                    states = evolve_generator(pattern)
                    time = math.inf
                elif event.key == pygame.K_s and step_speed is math.inf:
                    state, index = next(states)

        time += elapsed
        if time >= step_speed:
            time = 0
            state, index = next(states)

        # draw
        screen.fill('black')

        state_rects = [
            copyrect(cell, x=col*cell.width, y=row*cell.height) for row, col in state
        ]

        _cellsrect = wraprects(state_rects)
        if any(it.starmap(op.gt, zip(_cellsrect.size, cellsrect.size))):
            cellsrect.size = tuple(it.starmap(max, zip(_cellsrect.size, cellsrect.size)))
            cellsrect.center = frame.center

            gridlines.clear()
            xs = range(cellsrect.x % cell.width, frame.right, cell.width)
            ys = range(cellsrect.y % cell.height, frame.bottom, cell.height)
            for x, y in it.product(xs, ys):
                start = (frame.left, y)
                end = (frame.right, y)
                gridlines.add((start, end))

                start = (x, frame.top)
                end = (x, frame.bottom)
                gridlines.add((start, end))

        for rect in state_rects:
            rect.topleft += pygame.Vector2(cellsrect.topleft)
            pygame.draw.rect(screen, styles.cells.foreground, rect)

        for start, end in gridlines:
            pygame.draw.line(screen, styles.grid.foreground, start, end)

        lines = [
            f'is_stepping={step_speed is math.inf}',
            f'{len(state)=}',
            f'{index=}',
            f'{frame_number=}',
            f'fps={clock.get_fps():.0f}',
        ]
        images = list(render_lines(font, lines, styles.text.foreground))
        rects = [image.get_rect() for image in images]

        for r1, r2 in it.pairwise(rects):
            r2.topright = r1.bottomright
        subrect = wraprects(rects)
        subrect.topleft = (0, 0)
        align_as(rects, bottomright=subrect.bottomright)

        subsurf = pygame.Surface(subrect.size, flags=pygame.SRCALPHA)
        subsurf.fill(styles.text.background)
        for image, rect in zip(images, rects):
            subsurf.blit(image, rect)
        if styles.text.border_color:
            pygame.draw.rect(subsurf, styles.text.border_color, subsurf.get_rect(), 1)
        rect = subsurf.get_rect(bottomright=frame.inflate((-8,)*2).bottomright)
        screen.blit(subsurf, rect)

        pygame.display.update()

        frame_number += 1

class sizetype:

    def __init__(self, n):
        self.n = n

    def __call__(self, s):
        dimensions = list(map(int, s.replace(',', ' ').split()))
        while len(dimensions) < self.n:
            dimensions.append(dimensions[-1])
        return dimensions

def main(argv=None):
    """
    Animated game of life.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('pattern', choices=['blinker', 'angel', 'washing_machine'])
    parser.add_argument('--step', type=int)
    parser.add_argument('--size', type=sizetype(2), default='30')
    args = parser.parse_args(argv)
    pattern_func = getattr(patterns, args.pattern)
    pattern = pattern_func()
    run(pattern, args.size, args.step)

if __name__ == '__main__':
    main()

