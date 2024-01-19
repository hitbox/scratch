import argparse
import code
import contextlib
import functools
import io
import itertools as it
import math
import operator as op
import sys
import textwrap
import unittest

import pygamelib

from pygamelib import pygame

try:
    sys.ps1
except AttributeError:
    sys.ps1 = '>>> '

try:
    sys.ps2
except AttributeError:
    sys.ps2 = '... '

class InteractiveConsole(code.InteractiveConsole):
    """
    InteractiveConsole that saves output into a list.
    """

    def __init__(self, locals=None):
        super().__init__(locals=locals)
        self.stdout = []

    def runcode(self, code):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            super().runcode(code)
            self._stdout(stdout.getvalue())

    def write(self, data):
        self._stdout(data)

    def _stdout(self, text):
        self.stdout.extend(text.splitlines())


class Ticker:

    def __init__(self, length, start=0):
        self.length = length
        self.index = start

    def update(self, advance=1):
        self.index = (self.index + advance) % self.length


class Editor(pygamelib.DemoBase):

    def __init__(self, shapes=None):
        if shapes is None:
            shapes = []
        self.shapes = shapes
        self.font = pygame.font.SysFont('monospace', 18)
        self.text_color = 'white'
        self.caret_image = pygame.Surface(self.font.size(' '))
        self.caret_image.fill(self.text_color)
        self.caret_blink = Ticker(60)
        self.interactive = InteractiveConsole(
            locals = dict(
                editor = self,
                shapes = self.shapes,
                circle = self.create_circle,
            ),
        )
        self.readline = pygamelib.Readline(self._read_input)
        self.text_wrapper = textwrap.TextWrapper()

    def create_circle(self, color, position, radius):
        try:
            pygame.Color(color)
        except ValueError:
            self.interactive.showtraceback()
            return
        self.shapes.append(('circle', color, position, radius))

    def _read_input(self, line):
        # save input line with prompt to "stdout"
        self.interactive.write(self.readline.full_input_line())
        # evaluate line
        self.readline.more = self.interactive.push(line)

    def start(self, engine):
        super().start(engine)
        self.console_rect = self.window.copy()
        scale = 4
        size = tuple(map(lambda value: value / scale, self.window.size))
        self.buffer = pygame.Surface(size)

    def update(self):
        super().update()
        self.caret_blink.update()
        self.draw()

    def do_quit(self, event):
        self.engine.stop()

    def __do_keydown(self, event):
        pygamelib.dispatch(self.readline, event)
        pygamelib.post_videoexpose()

    def draw_shapes(self, surf):
        for shape, color, *args in self.shapes:
            func = getattr(pygame.draw, shape, None)
            func(surf, color, *args)

    def _console_lines(self):
        for line in self.interactive.stdout:
            for wrapped_line in self.text_wrapper.wrap(line):
                yield wrapped_line

    def _lines_for_draw(self):
        lines = list(self._console_lines()) + [self.readline.full_input_line()]
        return lines

    def draw_interactive(self):
        lines = self._lines_for_draw()
        images, rects = pygamelib.make_blitables_from_font(lines, self.font, self.text_color)
        lines_rect = pygame.Rect(pygamelib.wrap(rects))
        if not self.console_rect.contains(lines_rect):
            pygamelib.move_as_one(rects, bottomleft=self.console_rect.bottomleft)
        pygame.draw.rect(self.screen, self.text_color, lines_rect, 1)
        for image, rect in zip(images, rects):
            if self.console_rect.colliderect(rect):
                self.screen.blit(image, rect)

        # blinking caret
        if self.caret_blink.index < self.framerate / 2:
            input_line = self.readline.input_lines[self.readline.input_index]
            before_text, after_text = input_line.split()
            offsetx, offsety = self.font.size(self.readline.prompt() + before_text)
            caret_rect = self.caret_image.get_rect(
                left = rects[-1].left + offsetx,
                bottom = rects[-1].bottom,
            )
            self.screen.blit(self.caret_image, caret_rect)

    def draw(self):
        self.screen.fill('black')
        self.draw_shapes(self.screen)
        #self.draw_interactive()
        #pygame.transform.scale(self.buffer, self.window.size, self.screen)
        pygame.display.flip()

    def do_videoexpose(self, event):
        self.draw()


def run(screen_size, shapes, scale, offset):
    pygame.font.init()
    font = pygame.font.SysFont('monospace', 20)
    editor = ShapeBrowser(font, scale, offset, shapes)
    engine = pygamelib.Engine()
    pygame.display.set_mode(screen_size)
    engine.run(editor)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'shapes',
        type = argparse.FileType(),
    )
    parser.add_argument(
        '--scale',
        type = int,
        default = 1,
        help = 'Scale shapes',
    )
    parser.add_argument(
        '--screen-size',
        type = pygamelib.sizetype(),
        default = '800',
    )
    parser.add_argument(
        '--offset',
        type = pygamelib.sizetype(),
        default = '0',
    )
    args = parser.parse_args(argv)

    if args.shapes:
        shape_parser = pygamelib.ShapeParser()
        shapes = list(shape_parser.parse_file(args.shapes))
    else:
        shapes = None

    run(args.screen_size, shapes, args.scale, args.offset)

if __name__ == '__main__':
    main()
