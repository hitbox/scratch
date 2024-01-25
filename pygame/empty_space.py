import itertools as it
import operator as op
import random

from pprint import pprint

import pygamelib

from pygamelib import pygame

COLORS = list(filter(pygamelib.interesting_color, pygame.color.THECOLORS))
sides = op.attrgetter('top', 'right', 'bottom', 'left')

class Demo(pygamelib.DemoBase):

    def __init__(self, inside, rects_generator):
        self.inside = inside
        self.rects_generator = rects_generator
        self.rect_renderer = pygamelib.RectRenderer()
        self.update_rects()

    def update_rects(self):
        self.rects, self.empties = self.rects_generator(self.inside)

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.engine.stop()
        else:
            self.update_rects()
            pygamelib.post_videoexpose()

    def do_mousemotion(self, event):
        if event.buttons[0]:
            self.rect_renderer.offset += event.rel
            pygamelib.post_videoexpose()
        elif not any(event.buttons):
            for rect in self.rects + self.empties:
                if rect.collidepoint(event.pos):
                    self.rect_renderer.highlight = rect
                    pygamelib.post_videoexpose()
                    break
            else:
                self.rect_renderer.highlight = None

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        self.rect_renderer(self.screen, 'white', 0, self.rects)
        self.rect_renderer(self.screen, 'red', 1, self.empties)
        pygame.display.flip()


def find_empty_space(rectangles, inside):
    empties = [inside]
    for rect in rectangles:
        empties = list(map(pygame.Rect, subtract_rect(empties, rect)))
    return empties

def subtract_rect(empties, rect_to_subtract):
    for empty in empties:
        clip = empty.clip(rect_to_subtract)
        if not all(clip.size):
            # no intersection
            yield empty
            continue
        if empty.left < clip.left:
            # left rect
            yield (empty.left, empty.top, clip.left - empty.left, empty.height)
        if empty.right > clip.right:
            # right rect
            yield (clip.right, empty.top, empty.right - clip.right, empty.height)
        if empty.top < clip.top:
            # top rect
            minright = min(empty.right, clip.right)
            maxleft = max(empty.left, clip.left)
            yield (maxleft, empty.top, minright - maxleft, clip.top - empty.top)
        if empty.bottom > clip.bottom:
            # bottom rect
            minright = min(empty.right, clip.right)
            maxleft = max(empty.left, clip.left)
            yield (maxleft, clip.bottom, minright - maxleft, empty.bottom - clip.bottom)

def rect_from_points(x1, y1, x2, y2):
    return (x1, y1, x2 - x1, y2 - y1)

def rand_rect_point(rect):
    top, right, bottom, left = sides(rect)
    return (random.randint(left, right), random.randint(top, bottom))

def rand_endpoints(inside):
    return (*rand_rect_point(inside), *rand_rect_point(inside))

def random_rect(inside):
    endpoints = rand_endpoints(inside)
    rect = pygame.Rect(rect_from_points(*endpoints))
    rect.normalize()
    return rect

def random_rects(inside, nrects, minwidth=0, minheight=0):
    rects = []
    while nrects > 0:
        rect = random_rect(inside)
        if (
            rect.width > minwidth
            and
            rect.height > minheight
            and
            not any(other.colliderect(rect) for other in rects)
        ):
            yield rect
            rects.append(rect)
            nrects -= 1

class RectsGenerator:

    def __init__(self, n, minwidth, minheight):
        self.n = n
        self.minwidth = minwidth
        self.minheight = minheight

    def __call__(self, inside):
        rects = list(random_rects(inside, self.n, self.minwidth, self.minheight))
        # negative rects
        empty_space_rects = list(find_empty_space(rects, inside))
        assert empty_space_rects
        # because the rect subtraction function is not aware of already
        # "subtracted" rects, it generates excessive rects
        empty_space_rects = pygamelib.merge_all_rects(empty_space_rects)
        empty_space_rects = list(map(pygame.Rect, empty_space_rects))
        return (rects, empty_space_rects)


def run(display_size, nrects):
    window = pygame.Rect((0,)*2, display_size)
    space = window.inflate((-min(window.size)*.25,)*2)
    engine = pygamelib.Engine()
    state = Demo(space, RectsGenerator(nrects, 100, 100))
    pygame.display.set_mode(window.size)
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('--nrects', type=int, default=1)
    args = parser.parse_args(argv)

    if args.nrects > len(COLORS):
        parser.error('Invalid nrects')

    run(args.display_size, args.nrects)

if __name__ == '__main__':
    main()
