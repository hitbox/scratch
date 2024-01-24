import argparse
import itertools as it
import operator as op
import random

import pygamelib

from pygame import Vector2
from pygamelib import pygame

# extremity function for finding the random range limit
# needs a name
EXTREMES = [min, max, min, max]
OPPOKEYS = list(map(op.attrgetter, pygamelib.SIDENAMES_OPPO))
COMPS = [op.lt, op.gt, op.gt, op.lt]

class Demo(pygamelib.DemoBase):

    def __init__(self, n, frame, makerects, colors):
        self.n = n
        self.frame = frame
        self.makerects = makerects
        self.colors = colors
        self.rects = self.makerects(self.n, self.frame)
        self.highlight = None

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()
        else:
            self.rects = self.makerects(self.n, self.frame)
            pygamelib.post_videoexpose()

    def do_mousebuttondown(self, event):
        pygamelib.post_quit()

    def do_mousemotion(self, event):
        for rect in self.rects:
            if pygame.Rect(rect).collidepoint(event.pos):
                self.highlight = rect
                pygamelib.post_videoexpose()
                break
        else:
            self.highlight = None

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        self.draw_rects()
        pygame.display.flip()

    def draw_rects(self):
        for rect, color in zip(self.rects, self.colors):
            if rect is self.highlight:
                color = 'magenta'
            pygame.draw.rect(self.screen, color, rect, 0)


def random_touching_rects(n, frame):
    """
    Return a list of randomly generated, touching, non-overlapping rects.
    """
    assert n > 1
    mindim = 10
    walls = list(pygamelib.rectwalls(frame))
    rects = []
    while True:
        x = random.randint(frame.left, frame.right)
        y = random.randint(frame.top, frame.bottom)
        if frame.right - x > mindim and frame.bottom - y > mindim:
            w = random.randint(mindim, frame.right - x)
            h = random.randint(mindim, frame.bottom - y)
            rects.append((x, y, w, h))
            break
    attempts = 0
    while len(rects) < n and attempts < 10_000:
        reference = random.choice(rects)
        sidename = random.choice(pygamelib.SIDENAMES)
        side = getattr(pygame.Rect(reference), sidename)
        opposite_sidename = pygamelib.SIDES[sidename]
        opposite = op.attrgetter(opposite_sidename)
        nearestfunc = pygamelib.nearest_for_side[sidename]

        others = set(rects + walls)
        others.remove(reference)

        nearest_rect = nearestfunc(reference, others)
        if not nearest_rect:
            attempts += 1
            continue

        nearest_rect = pygame.Rect(nearest_rect)
        side_ = opposite(nearest_rect)
        if abs(side_ - side) < mindim:
            attempts += 1
            continue

        # check side is not one that would leave no space for a random rect
        tenths = random.randint(3, 9)
        newdim = side * (tenths / 10)
        randdim = random.randint(mindim, abs(side_ - side))
        # as if top or bottom was selected
        width, height = newdim, randdim
        if sidename in ('left', 'right'):
            # switch if not
            width, height = height, width
        newrect = pygame.Rect(0, 0, width, height)
        if sidename in ('top', 'bottom'):
            # random along left/right
            x, y, w, h = reference
            newrect.x = random.randint(x - w, x + w)
        else:
            # random along top/bottom
            x, y, w, h = reference
            newrect.y = random.randint(y - h, y + h)
        if sidename == 'top':
            newrect.bottom = side
        elif sidename == 'right':
            newrect.left = side
        elif sidename == 'bottom':
            newrect.top = side
        elif sidename == 'left':
            newrect.right = side
        # if no collisions append, otherwise loop trying again
        for _rect in rects + walls:
            if pygame.Rect(_rect).colliderect(newrect):
                attempts += 1
                break
        else:
            # stored as tuples for hashability
            rects.append(tuple(newrect))
    return rects

def run(display_size):
    frame = pygame.Rect((0,)*2, display_size)
    frame.inflate_ip((-min(display_size)*0.5,)*2)
    colors = list(filter(pygamelib.interesting_color, pygame.color.THECOLORS))
    random.shuffle(colors)
    state = Demo(
        50,
        frame,
        random_touching_rects,
        colors,
    )
    pygame.display.set_mode(display_size)
    engine = pygamelib.Engine()
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args.display_size)

if __name__ == '__main__':
    main()
