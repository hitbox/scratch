import argparse
import itertools as it
import operator as op
import random

import pygamelib

from pygame import Vector2
from pygamelib import pygame

SIDENAMES = ['top', 'right', 'bottom', 'left']
SIDEOPPOS = [SIDENAMES[(i+1)%len(SIDENAMES)] for i, n in enumerate(SIDENAMES)]

# extremity function for finding the random range limit
# needs a name
NAMEME = [max, min, min, max]

OPPOKEYS = list(map(op.attrgetter, SIDEOPPOS))
COMPS = [op.lt, op.gt, op.gt, op.lt]

class Demo(pygamelib.DemoBase):

    def __init__(self, n, frame, makerects):
        self.n = n
        self.frame = frame
        self.makerects = makerects
        self.rects = self.makerects(self.n, self.frame)

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

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        self.draw_rects()
        pygame.display.flip()

    def draw_rects(self):
        for rect in self.rects:
            pygame.draw.rect(self.screen, 'azure', rect, 1)


def random_touching_rects(n, frame):
    assert n > 1
    rects = []
    while True:
        x = random.randint(frame.left, frame.right)
        y = random.randint(frame.top, frame.bottom)
        if frame.right - x > 0 and frame.bottom - y > 0:
            w = random.randint(1, frame.right - x)
            h = random.randint(1, frame.bottom - y)
            if w > 0 and h > 0:
                rects.append(pygame.Rect(x, y, w, h))
                break
    walls = list(map(pygame.Rect, pygamelib.rectwalls(frame)))
    while len(rects) < n:
        rect = random.choice(rects)
        sideindex, sidename = random.choice(list(enumerate(SIDENAMES)))
        side = getattr(rect, sidename)
        getside = op.attrgetter(sidename)
        extreme = NAMEME[sideindex]
        key = OPPOKEYS[sideindex]
        comp = COMPS[sideindex]
        def predicate(other):
            return comp(key(other), side)

        # TODO
        # - probably also need to filter rects for being in the path of our new
        #   random rect
        others = list(map(key, filter(predicate, rects+walls)))
        if not others:
            continue
        side_ = extreme(others)
        if abs(side_ - side) < 10:
            continue

        # check side is not one that would leave no space for a random rect
        tenths = random.randint(3, 9)
        newdim = side * (tenths / 10)
        randdim = random.randint(10, abs(side_ - side))
        # as if top or bottom was selected
        width, height = newdim, randdim
        if sidename in ('left', 'right'):
            # switch if not
            width, height = height, width
        newrect = pygame.Rect(0, 0, width, height)
        if sidename in ('top', 'bottom'):
            newrect.x = random.randint(rect.left - newrect.width, rect.right)
        else:
            newrect.y = random.randint(rect.top - newrect.height, rect.bottom)
        if sidename == 'top':
            newrect.bottom = side
        elif sidename == 'right':
            newrect.left = side
        elif sidename == 'bottom':
            newrect.top = side
        elif sidename == 'left':
            newrect.right = side
        # if no collisions append, otherwise loop trying again
        for _rect in rects:
            if _rect.colliderect(newrect):
                break
        else:
            rects.append(newrect)
    return rects

def run(display_size):
    frame = pygame.Rect((0,)*2, display_size)
    frame.inflate_ip((-min(display_size)*0.5,)*2)
    state = Demo(10, frame, random_touching_rects)
    pygame.display.set_mode(display_size)
    engine = pygamelib.Engine()
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args.display_size)

if __name__ == '__main__':
    main()
