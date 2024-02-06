import argparse
import collections
import itertools as it
import pickle

import pygamelib

from pygamelib import pygame

class Touches(pygamelib.DemoBase):
    """
    Hover to demo touching rects.
    """

    def __init__(self, rects):
        self.rects = rects
        self.hovering = None
        self.touching = set()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()

    def do_videoexpose(self, event):
        self.draw()

    def do_mousemotion(self, event):
        for rect in self.rects:
            if pygame.Rect(rect).collidepoint(event.pos):
                self.hovering = rect
                self.touching = set(
                    other for other in self.rects
                    if other is not rect
                    and pygamelib.touch_relation(rect, other)
                )
                break
        else:
            self.hovering = None
            self.touching = set()
        self.draw()

    def draw(self):
        self.screen.fill('black')
        for rect in self.rects:
            if rect in self.touching or rect is self.hovering:
                width = 0 # fill
            else:
                width = 1
            color = 'orange' if rect is self.hovering else 'darkorange4'
            pygame.draw.rect(self.screen, color, rect, width)
        pygame.display.flip()


def main(argv=None):
    """
    Find islands of rects.
    """
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'rects',
        type = argparse.FileType('rb'),
        help = 'Pickle file list of rects.',
    )
    args = parser.parse_args(argv)
    rects = pickle.load(args.rects)
    state = Touches(rects)
    engine = pygamelib.Engine()
    pygame.display.set_mode(args.display_size)
    engine.run(state)

if __name__ == '__main__':
    main()

# 2024-02-06 Tue.
# - find rects that touch
# - group rects into "islands" where there is a path to every other rect by way
#   of their touching sides
# - motivation: pygamelib.generate_contiguous is broken, it returns results for
#   rects that are not touching
