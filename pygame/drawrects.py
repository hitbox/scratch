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

    def collidepoint_rects(self, point):
        for rect in self.state.rects:
            if pygame.Rect(rect).collidepoint(point):
                yield rect

    def do_mousemotion(self, event):
        if not any(event.buttons):
            self.do_mousemotion_nobuttons(event)
        elif event.buttons[0]:
            self.state.drag_offset(event.rel)
            self.state.draw()

    def do_mousemotion_nobuttons(self, event):
        handles = self.state.size_handles + self.state.move_handles
        handles = (handle for _, handle, _ in handles)
        any_handle = any(handle.collidepoint(event.pos) for handle in handles)
        if not any_handle:
            self.state.hovering = list(self.collidepoint_rects(event.pos))
            self.state.update_handles()

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
        self.state.update_handles()
        self.state.update_images()
        self.state.draw()


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
        self.state.update_handles()
        self.state.draw()


class RectEditor(pygamelib.DemoBase):

    def __init__(self):
        self.controllers = [self, HoverController(self)]
        self.offset = pygame.Vector2()
        self.rects = []
        self.images = []
        self.hovering = []
        self.move_handles = []
        self.size_handles = []
        self.handle_width = 20
        self.get_resize_handles = pygamelib.rect_handles_outside
        self.update_images()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.engine.stop()

    def do_videoexpose(self, event):
        self.draw()

    def drag_offset(self, relative):
        self.offset += relative

    def update_handles(self):
        if not self.hovering:
            self.size_handles.clear()
            self.move_handles.clear()
        else:
            # set resize handle rects
            self.size_handles = list(
                (rect, pygame.Rect(handle), name)
                for rect in self.hovering
                for handle, name in zip(
                    self.get_resize_handles(rect, self.handle_width),
                    pygamelib.HANDLE_NAMES
                )
            )
            # set move handle rects
            self.move_handles = [
                (
                    rect,
                    pygame.Rect(pygamelib.move_handle(rect, self.handle_width)),
                    'center',
                )
                for rect in self.hovering
            ]
        self.draw()

    def iter_images_for_rects(self):
        for index, rect in enumerate(self.rects):
            image = pygame.Surface(rect.size, pygame.SRCALPHA)
            reverse = index % 2 == 0
            _rect = (0,0,*rect.size)
            lines = pygamelib.rect_diagonal_lines(_rect, (8,)*2, reverse=reverse)
            color = self.color_for_rect(rect)
            for line in lines:
                pygame.draw.line(image, color, *line, 1)
            yield image

    def update_images(self):
        self.images = list(self.iter_images_for_rects())

    def color_for_rect(self, rect):
        if rect in self.hovering:
            color = 'orange'
        else:
            color = 'grey30'
        return color

    def draw(self):
        self.screen.fill('black')
        self.draw_rects()
        self.draw_handles()
        pygame.display.flip()

    def draw_rects(self):
        for rect, image in zip(self.rects, self.images):
            rect = rect.move(self.offset)
            self.screen.blit(image, rect)
            color = self.color_for_rect(rect)
            pygame.draw.rect(self.screen, color, rect, 1)

    def draw_handles(self):
        for rect, handle, name in self.size_handles + self.move_handles:
            handle = handle.move(self.offset)
            pygame.draw.rect(self.screen, 'darkred', handle, 1)


# XXX
# - above: way too much going on for something called drawrects
# - below: simplified main but keeping old code just in case
# TODO
# - decide what to keep
# - probably not much as this was probably supposed to stay a simple script to
#   display rects

def run(display_size, framerate, background, rects):
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill(background)
        for rect in rects:
            pygame.draw.rect(screen, 'white', rect, 1)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('rects', type=argparse.FileType('r'))
    args = parser.parse_args(argv)

    rects = list(map(pygamelib.rect_type, args.rects))
    run(args.display_size, args.framerate, args.background, rects)

def main_trash():
    pygame.display.init()
    pygame.font.init()
    engine = pygamelib.Engine()
    state = RectEditor()

    state.rects = rects.copy()
    state.update_images()

    pygame.display.set_mode(window.size)
    engine.run(state)

    pygame.quit()
    if rects != state.rects:
        if input(f'save {args.rects.name}? ').lower().startswith('y'):
            with open(args.rects.name, 'wb') as output_file:
                pickle.dump(state.rects, output_file)

if __name__ == '__main__':
    main()
