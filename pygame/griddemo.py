import argparse
import math

import pygamelib

from pygamelib import pygame

class GridDemo(pygamelib.BrowseBase):

    def __init__(self, blits, offset=None):
        self._blits = blits
        if offset is None:
            offset = pygame.Vector2()
        self.offset = offset


def run(rects, ncols, colattr, rowattr, show_labels):
    pygame.font.init()
    font = pygame.font.SysFont('monospace', 20)

    def _render(index, rect):
        result = pygame.Surface(rect.size)
        rect = result.get_rect()
        pygame.draw.rect(result, 'red', rect, 1)
        if show_labels:
            j, i = divmod(index, ncols)
            text = f'{j},{i}'
            text = font.render(text, True, 'white')
            result.blit(text, text.get_rect(center=rect.center))
        return result

    images = list(map(_render, *zip(*enumerate(rects))))
    pygamelib.arrange_columns(rects, ncols, colattr, rowattr)

    window = pygame.Rect((0,)*2, (800,)*2)
    blits = list(zip(images, rects))
    demo = GridDemo(blits, pygamelib.centered_offset(rects, window))
    pygame.display.set_mode(window.size)
    engine = pygamelib.Engine()
    engine.run(demo)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('rects', nargs='+', type=pygamelib.rect_type)
    parser.add_argument('--colattr', default='left')
    parser.add_argument('--rowattr', default='top')
    parser.add_argument('--columns', type=int)
    parser.add_argument('--no-labels', action='store_true')
    args = parser.parse_args(argv)

    if args.columns:
        ncols = args.columns
    else:
        ncols = math.isqrt(len(args.rects))

    run(args.rects, ncols, args.colattr, args.rowattr, not args.no_labels)

if __name__ == '__main__':
    main()
