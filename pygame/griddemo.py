import argparse
import heapq
import itertools as it
import math
import random

import pygamelib

from pygamelib import pygame

class GridDemo:

    def __init__(self, rects, ncols):
        self.rects = rects
        self.ncols = ncols
        self.clock = pygame.time.Clock()
        self.framerate = 60

    def start(self, engine):
        self.engine = engine
        self.screen = pygame.display.get_surface()
        self.window = self.screen.get_rect()
        self.font = pygame.font.SysFont('monospace', 20)
        _wrapped = pygame.Rect(pygamelib.wrap(self.rects))
        _positioned = pygamelib.make_rect(_wrapped, center=self.window.center)
        self.offset = pygame.Vector2(_positioned.topleft)
        self.rect_images = [self.font.render(f'{divmod(index, self.ncols)}', True, 'white') for index, _ in enumerate(self.rects)]

    def update(self):
        elapsed = self.clock.tick(self.framerate)
        for event in pygame.event.get():
            pygamelib.dispatch(self, event)
        self.screen.fill('black')
        for rect, image in zip(self.rects, self.rect_images):
            rect = pygame.Rect(rect.topleft + self.offset, rect.size)
            if self.window.colliderect(rect):
                pygame.draw.rect(self.screen, 'red', rect, 1)
                self.screen.blit(image, image.get_rect(center=rect.center))

        offset = tuple(map(int, self.offset))
        lines = [
            f'{offset=}',
            f'{self.clock.get_fps()=:.2f}',
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
            self.offset += event.rel


def nrandint(a, b, n):
    for _ in range(n):
        yield random.randint(a, b)

def run(nrects, a, b, colattr, rowattr):
    sizes = list(tuple(nrandint(a, b, 2)) for _ in range(nrects))
    rects = [pygame.Rect((0,)*2, size) for size in sizes]
    ncols = math.isqrt(len(rects))
    pygamelib.arrange_columns(rects, ncols, colattr, rowattr)

    demo = GridDemo(rects, ncols)

    pygame.display.set_mode((800,)*2)
    pygame.font.init()

    engine = pygamelib.Engine()
    engine.run(demo)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--nrects', type=int, default='20')
    parser.add_argument('--min', type=int, default='50')
    parser.add_argument('--max', type=int, default='100')
    parser.add_argument('--colattr', default='left')
    parser.add_argument('--rowattr', default='top')
    args = parser.parse_args(argv)
    run(args.nrects, args.min, args.max, args.colattr, args.rowattr)

if __name__ == '__main__':
    main()
