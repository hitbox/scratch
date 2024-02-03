import itertools as it
import math
import time

import pygamelib

from pygamelib import pygame

class Stat:

    def __init__(self):
        self.minval = +math.inf
        self.maxval = -math.inf

    def update(self, value):
        if value < self.minval:
            self.minval = value
        if value > self.maxval:
            self.maxval = value


class Blits(pygamelib.DemoBase):

    def __init__(self, display_size, tilesize, font):
        self.display_size = display_size
        self.tilesize = tilesize
        self.font = font
        self.fps_stats = Stat()
        self.update_blits()

    def update_blits(self):
        self.tile = pygame.Surface(self.tilesize)
        pygame.draw.circle(
            self.tile,
            'red',
            self.tile.get_rect().center,
            min(self.tilesize)/4
        )
        window_width, window_height = self.display_size
        tile_width, tile_height = self.tilesize

        self.blits = list(zip(
            it.repeat(self.tile),
            it.product(
                range(0, window_width, tile_width),
                range(0, window_height, tile_height)
            )
        ))

    def update(self):
        self.clock.tick()
        for event in pygame.event.get():
            pygamelib.dispatch(self, event)
        pygamelib.post_videoexpose()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        self.screen.blits(self.blits)
        fps = self.clock.get_fps()
        self.fps_stats.update(fps)
        lines = (
            f'fps={fps:04.0f}',
            f'minfps={self.fps_stats.minval:04.0f}',
            f'maxfps={self.fps_stats.maxval:04.0f}',
        )
        images, rects = pygamelib.make_blitables_from_font(lines, self.font, 'azure')
        self.screen.blits(zip(images, rects))
        pygame.display.flip()


def run(display_size, tile_size):
    font = pygamelib.monospace_font(30)
    state = Blits(display_size, tile_size, font)
    pygame.display.set_mode(display_size)
    engine = pygamelib.Engine()
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'tile_size',
        type = pygamelib.sizetype(),
    )
    args = parser.parse_args(argv)
    run(args.display_size, args.tile_size)

if __name__ == '__main__':
    main()
