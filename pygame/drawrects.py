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


class HoverController:

    def __init__(self, state):
        self.state = state
        self.get_resize_handles = pygamelib.rect_handles_outside
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
        handles = self.state.size_handles + self.state.move_handles
        handles = (handle for _, handle, _ in handles)
        if not any(handle.collidepoint(event.pos) for handle in handles):
            # not hovering any handles
            self.state.hovering = list(self.collidepoint_rects(event.pos))
            self.update_handles()

    def update_handles(self):
        if not self.state.hovering:
            self.state.size_handles.clear()
            self.state.move_handles.clear()
        else:
            # set resize handle rects
            self.state.size_handles = list(
                (rect, pygame.Rect(handle), name)
                for rect in self.state.hovering
                for handle, name in zip(
                    self.get_resize_handles(rect, self.handle_width),
                    pygamelib.HANDLE_NAMES
                )
            )
            # set move handle rects
            self.state.move_handles = [
                (
                    rect,
                    pygame.Rect(pygamelib.move_handle(rect, self.handle_width)),
                    'center',
                )
                for rect in self.state.hovering
            ]
            pygamelib.post_videoexpose()

    def do_mousebuttondown(self, event):
        if event.button == pygame.BUTTON_LEFT:
            self.do_mousebuttondown_leftclick(event)

    def state_handles_with_class(self):
        for rect, handle, name in self.state.size_handles:
            yield (rect, handle, name, ResizeHandleDragController)
        for rect, handle, name in self.state.move_handles:
            yield (rect, handle, name, MoveHandleDragController)

    def do_mousebuttondown_leftclick(self, event):
        items = self.state_handles_with_class()
        for rect, handle, name, controller_class in items:
            if not handle.collidepoint(event.pos):
                continue
            controller = controller_class(self.state, rect, handle, name)
            self.state.controllers.append(controller)


class ResizeHandleDragController:

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
