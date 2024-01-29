import itertools as it
import math
import os
import pickle

from pprint import pprint

import pygamelib

from pygamelib import pygame

class Snap:

    def __init__(self, threshold):
        self.threshold = threshold

    def __call__(self, value, *others):

        def key(other):
            return abs(other - value)

        def predicate(other):
            return key(other) < self.threshold

        return sorted(filter(predicate, others), key=key)


class Drag:

    def __init__(self):
        self.reset()

    def reset(self):
        self.start = None
        self.end = None

    def get_rect(self):
        x1, y1 = self.start
        x2, y2 = self.end
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        return (x1, y1, x2 - x1, y2 - y1)


class RectCornerDrag:

    def __init__(self, rect, corner_name):
        self.rect = rect
        self.corner_name = corner_name

    def get_rect(self, pos):
        pass


class Demo(pygamelib.DemoBase):

    def __init__(self):
        self.rects = []
        self.drag = Drag()
        self.rect_corner_drag = None
        self.snap = Snap(20)
        self.contiguous_rects = None
        self.contiguous_index = None
        self.savepath = None

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.engine.stop()
        elif event.key == pygame.K_g:
            self.generate_contiguous_rects()
        elif event.key == pygame.K_s:
            if self.savepath:
                with open(self.savepath, 'wb') as savefile:
                    pickle.dump(self.rects, savefile)
        elif event.key in (pygame.K_RIGHT, pygame.K_LEFT):
            if self.contiguous_rects:
                if event.key == pygame.K_RIGHT:
                    di = +1
                else:
                    di = -1
                self.contiguous_index = (
                    (self.contiguous_index + di) % len(self.contiguous_rects)
                )
                contrect = self.contiguous_rects[self.contiguous_index]
                pygamelib.post_videoexpose()

    def do_mousebuttondown(self, event):
        if event.button == pygame.BUTTON_LEFT:
            for rect in self.rects:
                names = ['top', 'right', 'bottom', 'left']
                for name, corner in zip(names, pygamelib.corners(rect)):
                    if math.dist(event.pos, corner) < self.snap.threshold:
                        self.rect_corner_drag = RectCornerDrag(rect, name)
                        break
                else:
                    continue
                break
            else:
                # no rect corner clicks
                self.drag.start = event.pos
                pygamelib.post_videoexpose()

    def generate_contiguous_rects(self):
        rects = pygamelib.generate_contiguous(self.rects)
        self.contiguous_rects = sorted(rects, key=pygamelib.area, reverse=True)
        self.contiguous_index = 0

    def do_mousebuttonup(self, event):
        if event.button == pygame.BUTTON_LEFT:
            if self.drag.start and self.drag.end:
                self.rects.append(self.drag.get_rect())
                self.drag.reset()
                self.generate_contiguous_rects()
                pygamelib.post_videoexpose()

    def do_mousemotion(self, event):
        if not any(event.buttons):
            pass
        elif event.buttons[0]:
            mx, my = event.pos
            for rect in self.rects:
                top, right, bottom, left = pygamelib.sides(rect)
                possiblex = self.snap(mx, right, left)
                if possiblex:
                    mx = possiblex[0]
                possibley = self.snap(my, top, bottom)
                if possibley:
                    my = possibley[0]
            self.drag.end = (mx, my)
            pygamelib.post_videoexpose()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        if self.contiguous_rects:
            contiguous_rect = self.contiguous_rects[self.contiguous_index]
            pygame.draw.rect(self.screen, 'brown', contiguous_rect, 0)
        for rect in self.rects:
            pygame.draw.rect(self.screen, 'azure', rect, 1)
        if self.drag.start and self.drag.end:
            rect = self.drag.get_rect()
            pygame.draw.rect(self.screen, 'magenta', rect, 1)
        pygame.display.flip()


def run(display_size, savepath):
    window = pygame.Rect((0,0), display_size)
    pygame.display.init()
    pygame.font.init()
    engine = pygamelib.Engine()
    state = Demo()

    if savepath:
        state.savepath = savepath
        if os.path.exists(savepath):
            with open(savepath, 'rb') as savefile:
                state.rects = pickle.load(savefile)
                state.generate_contiguous_rects()

    pygame.display.set_mode(display_size)
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('--pickle')
    args = parser.parse_args(argv)
    run(args.display_size, args.pickle)

if __name__ == '__main__':
    main()
