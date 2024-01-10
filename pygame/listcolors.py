import argparse
import itertools as it
import math
import random
import re

from pprint import pprint

import pygamelib

from pygamelib import pygame

from pygame.color import THECOLORS

class ColorGrid(pygamelib.BrowseBase):

    def __init__(self, blits, offset=None):
        self._blits = blits
        if offset is None:
            offset = pygame.Vector2()
        self.offset = offset


def _arrange(rects):
    # needed to pull the arrange_columns function apart to add gaps and resize
    # the arranged rects
    ncols = math.isqrt(len(rects)) // 2
    rows, cols = pygamelib.groupby_columns(rects, ncols)
    row_wraps, col_wraps = pygamelib.rowcolwraps(rows, cols)

    for rowwrap in row_wraps:
        rowwrap.height *= 4

    for colwrap in col_wraps:
        colwrap.width *= 1.10

    pygamelib.flow_topbottom(row_wraps, 20)
    pygamelib.flow_leftright(col_wraps, 20)

    for rowwrap, _rects in zip(row_wraps, rows, strict=True):
        for rect in _rects:
            rect.height = rowwrap.height
            rect.centery = rowwrap.centery

    for colwrap, _rects in zip(col_wraps, cols, strict=True):
        for rect in _rects:
            rect.width = colwrap.width
            rect.left = colwrap.left

def run(size, colors, names, font_size):
    assert len(colors) == len(names)
    pygame.font.init()
    font = pygame.font.SysFont('monospace', font_size)

    rects = [pygame.Rect((0,)*2, font.size(name)) for name in names]
    _arrange(rects)

    def _render_image(name, color, rect):
        color = pygame.Color(color)
        result = pygame.Surface(rect.size)
        result.fill(color)
        rect = result.get_rect()
        text = font.render(name, True, 'white', color.lerp('black', 0.5))
        result.blit(text, text.get_rect(center=rect.center))
        return result

    images = [
        _render_image(name, color, rect)
        for name, color, rect in zip(names, colors, rects)
    ]

    blits = list(zip(images, rects))
    window = pygame.Rect((0,)*2, size)
    demo = ColorGrid(blits, offset=pygamelib.centered_offset(rects, window))
    engine = pygamelib.Engine()

    pygame.display.set_mode(window.size)
    engine.run(demo)

def exclude_func(args):
    if not args.exclude and not args.colorful:
        exclude = lambda name: False
    elif args.exclude or args.colorful:
        if args.exclude:
            exclude = re.compile(args.exclude).search
        else:
            def exclude(name):
                return not pygamelib.interesting_color(name)
    return exclude

def unique(iterable, key=None):
    if key is None:
        def key(item):
            return item
    seen = set()
    for item in iterable:
        _key = key(item)
        if _key not in seen:
            seen.add(_key)
            yield item

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--screen-size',
        type = pygamelib.sizetype(),
        default = '1024',
    )
    parser.add_argument(
        '--font-size',
        type = int,
        default = '15',
    )
    parser.add_argument('--print', action='store_true')

    filtering_group = parser.add_mutually_exclusive_group()
    filtering_group.add_argument('--exclude')
    filtering_group.add_argument('--colorful', action='store_true')

    ordering_group = parser.add_mutually_exclusive_group()
    ordering_group.add_argument('--shuffle', action='store_true')
    for space_name in pygamelib.ColorSpace.spaces:
        ordering_group.add_argument(f'--{space_name}', action='store_true')
    args = parser.parse_args(argv)

    exclude = exclude_func(args)
    # XXX
    # - there are dupes in THECOLORS (?)
    colors = (color for name, color in THECOLORS.items() if not exclude(name))
    colors = list(map(pygame.Color, unique(colors, tuple)))

    if args.shuffle:
        random.shuffle(colors)
    else:
        for space_name in pygamelib.ColorSpace.spaces:
            flag = getattr(args, space_name)
            if flag:
                color_key = pygamelib.ColorSpace(space_name)
                colors = sorted(colors, key=color_key)
                break

    # TODO
    # - interactive filter
    # - colors generator
    # - class to render
    # - class to arrange grid

    names = list(map(pygamelib.color_name, colors))
    if args.print:
        pprint(names)

    run(args.screen_size, colors, names, args.font_size)

if __name__ == '__main__':
    main()
