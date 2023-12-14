import argparse
import contextlib
import itertools
import math
import os
import random

from itertools import groupby
from itertools import permutations
from operator import itemgetter
from string import digits
from types import SimpleNamespace

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class Style(SimpleNamespace):

    def __getattr__(self, key):
        return self.__dict__.get(key)

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


def deltas():
    # generate 3x3 neighbors deltas
    for i in range(9):
        row, col = divmod(i, 3)
        yield (row - 1, col - 1)

def pip_order(delta):
    row, col = delta
    is_corner = all(delta)
    return (-is_corner, -col, row)

def pip_angle(delta):
    row, col = delta
    angle = math.atan2(row, col) % math.pi
    return angle

def sorted_groupby(iterable, key=None, reverse=False):
    return groupby(sorted(iterable, key=key, reverse=reverse), key=key)

def update_with_reverse(dict_):
    dict_.update(list(map(reversed, dict_.items())))

def iteritems(iterable, *indexes):
    return map(itemgetter(*indexes), iterable)

def mapgroupiters(grouped, container=tuple):
    """
    containerize the group iterables as from itertools.groupby
    """
    return map(container, iteritems(grouped, 1))

def anyin(iterable, *subs):
    return any(sub in iterable for sub in subs)

def colorful(name):
    return (
        not anyin(name, 'grey', 'gray', 'white', 'black')
        and
        set(name).isdisjoint(digits)
        and
        name not in ('red', 'green', 'blue')
    )

COLORFUL = {name: rgba for name, rgba in pygame.color.THECOLORS.items() if colorful(name)}

DELTAS_WITH_ORIGIN = list(deltas())

PIP_DELTAS = sorted(DELTAS_WITH_ORIGIN, key=pip_order)
PIP_DELTAS.remove((0,0))

OPPOSITES = dict(mapgroupiters(sorted_groupby(PIP_DELTAS, key=pip_angle)))
update_with_reverse(OPPOSITES)

def is_odd(n):
    return n % 2 != 0

def iter_pip_deltas(n):
    if is_odd(n):
        yield (0, 0)
        n -= 1
        if n == 0:
            return
    seen = set()
    for delta in PIP_DELTAS:
        opposite = OPPOSITES[delta]
        if delta in seen or opposite in seen:
            continue
        seen.add(delta)
        seen.add(opposite)
        yield delta
        yield opposite
        if len(seen) == n:
            break

def mix(a, b, x):
    # numerically stable, less floating point errors
    return a * (1 - x) + b * x

def remap(a, b, c, d, x):
    return x*(d-c)/(b-a) + c-a*(d-c)/(b-a)

def iter_rect_ends(rect):
    # generate the dimensional extremes of a rect, its x and y endpoints
    yield (rect.left, rect.right)
    yield (rect.top, rect.bottom)

def remap_delta_xy(rowcol, rect):
    def _remap_dim(item):
        index, rectdim = item
        min_, max_ = rectdim
        return remap(-1, +1, min_, max_, index)
    pos = map(_remap_dim, zip(reversed(rowcol), iter_rect_ends(rect)))
    return tuple(pos)

def make_dicerect(dice_window, rowcol, dice_size, dice_border):
    row, col = rowcol
    # map from delta to screen/rect position
    remap_rect = dice_window.inflate((-(dice_border + dice_size),)*2)
    center = remap_delta_xy(rowcol, remap_rect)
    dice_rect = pygame.Rect(0, 0, dice_size, dice_size)
    dice_rect.center = center
    return dice_rect

    remap_rect = pygame.Rect(
        dice_window.left + dice_border,
        dice_window.top + dice_border,
        dice_window.width - dice_size - dice_border * 2,
        dice_window.height - dice_size - dice_border * 2,
    )
    x, y = remap_delta_xy(rowcol, remap_rect)
    dice_rect = pygame.Rect(x, y, dice_size, dice_size)
    return dice_rect

def piprect(dice_rect, pipsize, pippos, dice_border):
    """
    Rect for one of the pip positions inside a dice rect.
    """
    pip_width, pip_height = pipsize
    pip_row, pip_col = pippos
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
    return pip_rect

def run():
    pygame.font.init()
    screen = pygame.display.set_mode((800, 700))
    window = screen.get_rect()
    font = pygame.font.SysFont('monospace', 24)
    clock = pygame.time.Clock()
    framerate = 60

    reduction = -min(window.size) // 16
    dice_window = window.inflate((reduction,)*2)

    border_width = 4

    space_ratio_denom = 2 ** 4

    dice_margin = min(dice_window.size) // space_ratio_denom
    # NOTE
    # - denominator here dialed in manually
    dice_size = min(dice_window.size) // 3.05 - dice_margin

    dice_colors = random.sample(list(COLORFUL), 9)

    dice_list = list(range(1,10))

    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        screen.fill('black')
        pygame.draw.rect(screen, 'brown', dice_window, 1)

        for n, dicepos, color in zip(dice_list, DELTAS_WITH_ORIGIN, dice_colors):
            dice_rect = make_dicerect(dice_window, dicepos, dice_size, dice_margin)
            # fill
            pygame.draw.rect(screen, color, dice_rect)
            # border
            pygame.draw.rect(screen, 'azure', dice_rect, border_width)

            dice_border = min(dice_rect.size) // space_ratio_denom

            pip_width = (dice_rect.width // 3) - dice_border
            pip_height = (dice_rect.height // 3) - dice_border
            pip_size = (pip_width, pip_height)
            for pippos in iter_pip_deltas(n):
                pip_rect = piprect(dice_rect, pip_size, pippos, dice_border)
                radius = min(pip_rect.size) // 2
                # fill
                pygame.draw.circle(screen, 'azure', pip_rect.center, radius)
                # pip border with fake shading
                pygame.draw.circle(screen, 'grey', pip_rect.center, radius, border_width)
                pygame.draw.circle(screen, 'black', pip_rect.center, radius, border_width//2)

            # dice number text
            text_image = font.render(f'{n=}', True, 'azure')
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
