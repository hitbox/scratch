import argparse
import heapq
import itertools as it
import math
import random

import pygamelib

from pygamelib import pygame

class GridDemo:

    def __init__(self, rects, ncols, show_labels=False):
        self.rects = rects
        self.ncols = ncols
        self.show_labels = show_labels
        self.clock = pygame.time.Clock()
        self.framerate = 60

    def start(self, engine):
        self.engine = engine
        self.screen = pygame.display.get_surface()
        self.window = self.screen.get_rect()
        self.font = pygame.font.SysFont('monospace', 20)
        _wrapped = pygame.Rect(pygamelib.wrap(self.rects))
        _positioned = pygamelib.make_rect(self.window, center=_wrapped.center)
        self.offset = pygame.Vector2(_positioned.topleft)

        def _render(index):
            j, i = divmod(index, self.ncols)
            return self.font.render(f'{j},{i}', True, 'white')

        self.rect_images = [_render(index) for index, _ in enumerate(self.rects)]

    def update(self):
        self.clock.tick(self.framerate)
        for event in pygame.event.get():
            pygamelib.dispatch(self, event)

    def do_videoexpose(self, event):
        self.screen.fill('black')
        for rect, image in zip(self.rects, self.rect_images):
            rect = pygame.Rect(rect.topleft - self.offset, rect.size)
            if self.window.colliderect(rect):
                pygame.draw.rect(self.screen, 'red', rect, 1)
                if self.show_labels:
                    self.screen.blit(image, image.get_rect(center=rect.center))
        offset = tuple(map(int, self.offset))
        lines = [
            f'{offset=}',
        ]
        self.screen.blits(pygamelib.make_blitables_from_font(lines, self.font, 'white'))
        pygame.display.flip()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.quit()

    def do_mousemotion(self, event):
        if event.buttons[0]:
            self.offset -= event.rel
            pygame.event.post(pygame.event.Event(pygame.VIDEOEXPOSE))


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

    pygamelib.arrange_columns(args.rects, ncols, args.colattr, args.rowattr)
    demo = GridDemo(args.rects, ncols)

    pygame.display.set_mode((800,)*2)
    pygame.font.init()

    engine = pygamelib.Engine()
    engine.run(demo)

if __name__ == '__main__':
    main()
