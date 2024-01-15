import argparse
import code
import contextlib
import io
import itertools as it
import sys

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

class InteractiveInterpreter(code.InteractiveInterpreter):

    def __init__(self, locals=None):
        super().__init__(locals=locals)
        self.stdout = []

    def runcode(self, code):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            super().runcode(code)
            self.stdout.append(stdout.getvalue())

    def write(self, data):
        self.stdout.append(data)


class Editor(pygamelib.DemoBase):

    def __init__(self):
        self.font = pygame.font.SysFont('monospace', 24)
        self.chars = ''
        self.interactive = InteractiveInterpreter()
        self.more = False

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key == pygame.K_RETURN:
            self.more = self.interactive.runsource(self.chars)
            self.chars = ''
        elif event.key == pygame.K_BACKSPACE:
            self.chars = self.chars[:-1]
        else:
            self.chars += event.unicode
        pygamelib.post_videoexpose()

    def draw_line(self):
        if self.more:
            prompt = sys.ps2
        else:
            prompt = sys.ps1

        color = 'white'

        prompt_image = self.font.render(prompt, True, color)
        prompt_rect = prompt_image.get_rect(bottomleft=self.window.bottomleft)
        self.screen.blit(prompt_image, prompt_rect)

        line_image = self.font.render(self.chars, True, color)
        line_rect = line_image.get_rect(bottomleft=prompt_rect.bottomright)
        self.screen.blit(line_image, line_rect)

        if self.interactive.stdout:
            images, rects = pygamelib.make_blitables_from_font(
                self.interactive.stdout,
                self.font,
                color,
            )
            pygamelib.move_as_one(rects, bottomleft=prompt_rect.topleft)
            for image, rect in zip(images, rects):
                self.screen.blit(image, rect)

    def do_videoexpose(self, event):
        self.screen.fill('black')
        self.draw_line()
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
