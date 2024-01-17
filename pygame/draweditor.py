import argparse
import code
import contextlib
import io
import itertools as it
import sys
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

class TestInputLine(unittest.TestCase):

    def setUp(self):
        self.input_line = InputLine()

    def test_addchar(self):
        self.input_line.addchar('a')
        self.assertEqual(self.input_line.line, 'a')

    def test_insert_after_left(self):
        self.input_line.addchar('b')
        self.input_line.caretleft()
        self.input_line.addchar('a')
        self.assertEqual(self.input_line.line, 'ab')

    def test_insert_after_right(self):
        self.input_line.addchar('a')
        self.input_line.addchar('c')
        self.input_line.caretleft()
        self.input_line.caretleft()
        self.input_line.caretright()
        self.input_line.addchar('b')
        self.assertEqual(self.input_line.line, 'abc')

    def test_backspace(self):
        self.input_line.addchar('a')
        self.input_line.addchar('b')
        self.input_line.backspace()
        self.assertEqual(self.input_line.line, 'a')


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


class InputLine:

    def __init__(self, mode='insert'):
        self.line = ''
        self.caret = None
        self.mode = mode

    def split(self):
        if self.caret is None:
            return (self.line, '')
        else:
            return (self.line[:self.caret], self.line[self.caret:])

    def addchar(self, char):
        before, after = self.split()
        if self.mode == 'overwrite':
            self.line = before + char + after[1:]
        else:
            self.line = before + char + after

    def backspace(self):
        self.line = self.line[:-1]

    def caretleft(self):
        if self.caret is None:
            self.caret = len(self.line) - 1
        if self.caret > 0:
            self.caret -= 1

    def caretright(self):
        if self.caret is None:
            return
        self.caret += 1


class Ticker:

    def __init__(self, length, start=0):
        self.length = length
        self.index = start

    def update(self, advance=1):
        self.index = (self.index + advance) % self.length


class Editor(pygamelib.DemoBase):

    def __init__(self):
        self.font = pygame.font.SysFont('monospace', 18)
        self.more = False
        self.shapes = list()
        self.interactive = InteractiveConsole(locals=dict(shapes=self.shapes))
        self.caret_blink = Ticker(60)
        self.input_index = 0
        self.input_lines = [InputLine()]

    def start(self, engine):
        super().start(engine)
        self.console_rect = self.window.copy()

    def update(self):
        super().update()
        self.caret_blink.update()
        pygamelib.post_videoexpose()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key == pygame.K_RETURN:
            line = self.input_lines[self.input_index].line
            if line or self.more:
                self._read_input(line)
                self.input_lines[self.input_index] = line
                self.input_index += 1
                self.input_lines.append(InputLine())
        elif event.key == pygame.K_BACKSPACE:
            self.input_lines[self.input_index].backspace()
        elif event.key == pygame.K_UP:
            if self.input_index > 0:
                self.input_index -= 1
        elif event.key == pygame.K_DOWN:
            if self.input_index < len(self.input_lines) - 1:
                self.input_index += 1
        elif event.key == pygame.K_LEFT:
            self.input_lines[self.input_index].caretleft()
        elif event.key == pygame.K_RIGHT:
            self.input_lines[self.input_index].caretright()
        else:
            self.input_lines[self.input_index].addchar(event.unicode)

        pygamelib.post_videoexpose()

    def _read_input(self, line):
        echo = self._prompt() + line.rstrip()
        self.interactive.stdout.append(echo)
        self.more = self.interactive.push(line)

    def draw_shapes(self):
        for shape, color, *args in self.shapes:
            func = getattr(pygame.draw, shape)
            func(self.screen, color, *args)

    def _prompt(self):
        if self.more:
            return sys.ps2
        else:
            return sys.ps1

    def draw_interactive(self):
        color = 'white'
        lines = (
            self.interactive.stdout
            + [self._prompt() + self.input_lines[self.input_index].line]
        )
        images, rects = pygamelib.make_blitables_from_font(lines, self.font, color)
        lines_rect = pygame.Rect(pygamelib.wrap(rects))
        if not self.console_rect.contains(lines_rect):
            pygamelib.move_as_one(rects, bottomleft=self.console_rect.bottomleft)
        for image, rect in zip(images, rects):
            self.screen.blit(image, rect)

        # blinking caret
        if self.caret_blink.index < self.framerate / 2:
            caret_image = pygame.Surface(self.font.size(' '))
            caret_image.fill(color)
            caret_rect = caret_image.get_rect(bottomleft=rects[-1].bottomright)
            self.screen.blit(caret_image, caret_rect)

    def do_videoexpose(self, event):
        self.screen.fill('black')
        self.draw_shapes()
        self.draw_interactive()
        pygame.display.flip()


def run(screen_size):
    pygame.font.init()

    editor = Editor()

    engine = pygamelib.Engine()

    pygame.display.set_mode(screen_size)
    engine.run(editor)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--screen-size',
        type = pygamelib.sizetype(),
        default = '800',
    )
    args = parser.parse_args(argv)
    run(args.screen_size)

if __name__ == '__main__':
    main()
