import argparse
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
        """
        :param value: reference value
        :param others: other values to find nearest meeting threshold
        """

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


class DragController:

    def __init__(self, state):
        self.state = state


class ControllerTrash:

    def do_mousebuttondown(self, event):
        self.controller.do_mousebuttondown(event)

    def do_mousebuttonup(self, event):
        if event.button == pygame.BUTTON_LEFT:
            if self.drag.start and self.drag.end:
                self.rects.append(self.drag.get_rect())
                self.drag.reset()
                pygamelib.post_videoexpose()

    def do_mousemotion(self, event):
        mb1, mb2, mb3 = event.buttons
        if mb1:
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


class HoverController:

    def __init__(self, state):
        self.state = state
        self.get_handles = pygamelib.rect_handles_outside
        self.handle_width = 20

    def collidepoint_rects(self, point):
        for rect in self.state.rects:
            if pygame.Rect(rect).collidepoint(point):
                yield rect

    def do_mousemotion(self, event):
        if not any(event.buttons):
            self.do_mousemotion_nobuttons(event)
        else:
            # mouse motion while button is pressed
            # - dragging?
            pass

    def do_mousemotion_nobuttons(self, event):
        if any(handle.collidepoint(event.pos) for _, handle, _ in self.state.size_handles):
            # hovering a handle rect, leave the state alone
            pass
        else:
            self.state.hovering = list(self.collidepoint_rects(event.pos))
            if not self.state.hovering:
                self.state.size_handles.clear()
                self.state.move_handles.clear()
            else:
                # show handles on hover
                self.state.size_handles = list(
                    (rect, pygame.Rect(handle), name)
                    for rect in self.state.hovering
                    for handle, name in zip(
                        self.get_handles(rect, self.handle_width),
                        pygamelib.HANDLE_NAMES
                    )
                )
                self.state.move_handles = [
                    (rect, pygamelib.make_rect(size=(50,50), center=rect.center), 'center') for rect in self.state.hovering
                ]
                pygamelib.post_videoexpose()

    def do_mousebuttondown(self, event):
        if event.button == pygame.BUTTON_LEFT:
            for rect, handle, name in self.state.size_handles:
                if handle.collidepoint(event.pos):
                    controller = SizeHandleDragController(
                        self.state,
                        rect,
                        handle,
                        name,
                    )
                    # probably want to delay until after current frame events are handled
                    self.state.controllers.append(controller)
                    break
            for rect, handle, name in self.state.move_handles:
                if handle.collidepoint(event.pos):
                    controller = MoveHandleDragController(
                        self.state,
                        rect,
                        handle,
                        name,
                    )
                    self.state.controllers.append(controller)
                    break


class SizeHandleDragController:

    def __init__(self, state, rect, handle, name):
        self.state = state
        self.rect = rect
        self.handle = handle
        self.name = name
        assert self.name in pygamelib.HANDLE_NAMES

    def do_mousebuttonup(self, event):
        self.state.controllers.pop()

    def do_mousemotion(self, event):
        rx, ry = event.rel

        # lock sides movement
        if self.name in ('top', 'bottom'):
            rx = 0
        elif self.name in ('left', 'right'):
            ry = 0

        self.handle.move_ip((rx, ry))
        pygamelib.update_handle(self.rect, self.name, (rx, ry))
        pygamelib.post_videoexpose()


class MoveHandleDragController:

    def __init__(self, state, rect, handle, name):
        self.state = state
        self.rect = rect
        self.handle = handle
        self.name = name
        assert self.name == 'center'

    def do_mousebuttonup(self, event):
        self.state.controllers.pop()

    def do_mousemotion(self, event):
        self.handle.move_ip(event.rel)
        self.rect.move_ip(event.rel)
        pygamelib.post_videoexpose()


class Demo(pygamelib.DemoBase):

    def __init__(self):
        self.controllers = [HoverController(self)]
        self.rects = []
        self.hovering = []
        self.move_handles = []
        self.size_handles = []

    @property
    def controller(self):
        return self.controllers[-1]

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.engine.stop()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        for rect in self.rects:
            if rect in self.hovering:
                color = 'orange'
            else:
                color = 'grey30'
            pygame.draw.rect(self.screen, color, rect, 1)
        for rect, handle, name in self.size_handles + self.move_handles:
            pygame.draw.rect(self.screen, 'darkred', handle, 1)
        pygame.display.flip()


def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('rects', type=argparse.FileType('rb'))
    args = parser.parse_args(argv)

    rects = list(map(pygame.Rect, pickle.load(args.rects)))
    window = pygame.Rect((0,0), args.display_size)
    pygame.display.init()
    pygame.font.init()
    engine = pygamelib.Engine()
    state = Demo()
    state.rects = rects.copy()
    pygame.display.set_mode(window.size)
    engine.run(state)
    pygame.quit()
    if rects != state.rects:
        if input(f'save {args.rects.name}? ').lower().startswith('y'):
            with open(args.rects.name, 'wb') as output_file:
                pickle.dump(state.rects, output_file)

if __name__ == '__main__':
    main()
