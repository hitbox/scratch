import argparse
import contextlib
import itertools
import math
import os
import random

from itertools import groupby
from operator import itemgetter
from string import digits

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

def deltas():
    # generate 3x3 neighbors deltas
    for i in range(9):
        row, col = divmod(i, 3)
        yield (row - 1, col - 1)

def pip_order(delta):
    row, col = delta
    is_corner = all(delta)
    return (-is_corner, -col, row)

def delta_angle(delta):
    row, col = delta
    angle = math.atan2(row, col) % math.pi
    return angle

def paired(deltas):
    deltas = sorted(deltas, key=delta_angle)
    grouped = groupby(deltas, key=delta_angle)
    for _key, pairs in grouped:
        delta1, delta2 = pairs
        yield (delta1, delta2)
        yield (delta2, delta1)

def colorful(name):
    return (
        'grey' not in name
        and
        'gray' not in name
        and
        'white' not in name
        and
        'black' not in name
        and
        set(name).isdisjoint(digits)
    )

COLORFUL = {name: rgba for name, rgba in pygame.color.THECOLORS.items() if colorful(name)}

DELTAS_WITH_ORIGIN = list(deltas())

DELTAS = sorted(DELTAS_WITH_ORIGIN, key=pip_order)
DELTAS.remove((0,0))

OPPOSITES = dict(paired(DELTAS))

def iter_pip_deltas(n):
    if n % 2 != 0:
        yield (0, 0)
        n -= 1
        if n == 0:
            return
    seen = set()
    for delta in DELTAS:
        opposite = OPPOSITES[delta]
        if delta in seen or opposite in seen:
            continue
        yield delta
        yield opposite
        seen.add(delta)
        seen.add(opposite)
        if len(seen) == n:
            break

def mix(a, b, x):
    # numerically stable, less floating point errors
    return a * (1 - x) + b * x

def remap(a, b, c, d, x):
    return x*(d-c)/(b-a) + c-a*(d-c)/(b-a)

def iterdice():
    diceiter = sorted(enumerate(DELTAS_WITH_ORIGIN, start=1), key=itemgetter(0))
    for color, (n, (row, col)) in zip(COLORFUL, diceiter):
        yield (n, color, (row, col))

def dicerect(dice_window, rowcol, dice_size, dice_border):
    row, col = rowcol
    # map from delta to screen/rect position
    x = remap(
        -1, 1,
        dice_window.left + dice_border, dice_window.right - dice_size - dice_border,
        col
    )
    y = remap(
        -1, 1,
        dice_window.top + dice_border, dice_window.bottom - dice_size - dice_border,
        row
    )
    dice_rect = pygame.Rect(x, y, dice_size, dice_size)
    return dice_rect

def divrect(rect, denom, pin='topleft'):
    # NOTES
    # - was trying to make a func that would resize a rect so that a circle
    #   could be drawn inside it that would look like a shadow
    _rect = rect.copy()
    _rect.width /= denom
    _rect.height /= denom
    setattr(_rect, pin, getattr(rect, pin))
    return _rect

def run():
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    font = pygame.font.SysFont('monospace', 24)

    reduction = -min(window.size) // 16
    dice_window = window.inflate((reduction,)*2)

    border_width = 4

    space_ratio_denom = 2 ** 4

    dice_margin = min(dice_window.size) // space_ratio_denom
    # NOTE
    # - denominator here dialed in manually
    dice_size = min(dice_window.size) // 3.05 - dice_margin

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        screen.fill('black')
        pygame.draw.rect(screen, 'brown', dice_window, 1)

        for n, color, (dice_row, dice_col) in iterdice():
            dice_rect = dicerect(
                dice_window,
                (dice_row, dice_col),
                dice_size,
                dice_margin,
            )
            # fill
            pygame.draw.rect(screen, 'brown', dice_rect)
            # border
            pygame.draw.rect(screen, 'white', dice_rect, border_width)

            dice_border = min(dice_rect.size) // space_ratio_denom

            pip_width = (dice_rect.width // 3) - dice_border
            pip_height = (dice_rect.height // 3) - dice_border
            for (pip_row, pip_col) in iter_pip_deltas(n):
                x = remap(
                    -1,
                    +1,
                    dice_rect.left + dice_border,
                    dice_rect.right - pip_width - dice_border,
                    pip_col,
                )
                y = remap(
                    -1,
                    +1,
                    dice_rect.top + dice_border,
                    dice_rect.bottom - pip_height - dice_border,
                    pip_row,
                )
                pip_rect = pygame.Rect(x, y, pip_width, pip_height)
                radius = min(pip_rect.size) // 2
                # fill
                pygame.draw.circle(screen, 'white', pip_rect.center, radius)
                # border with fake shading
                pygame.draw.circle(screen, 'grey', pip_rect.center, radius, border_width)
                pygame.draw.circle(screen, 'black', pip_rect.center, radius, border_width//2)

            text_image = font.render(f'{n=}', True, 'white')
            screen.blit(text_image, text_image.get_rect(midtop=dice_rect.midbottom))

        pygame.display.flip()

def main(argv=None):
    """
    Draw dice pips algorithm
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()
