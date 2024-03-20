import argparse
import collections
import itertools as it
import pickle

import pygamelib

from pygamelib import pygame

class Touches(
    pygamelib.DemoBase,
    pygamelib.SimpleQuitMixin,
):
    """
    Hover to demo touching rects.
    """

    def __init__(self, rects, font, printer):
        self.rects = rects
        self.font = font
        self.printer = printer
        self.hovering = None
        self.touching = list()
        self.selected = list()

    def do_videoexpose(self, event):
        self.draw()

    def _find_rect(self, pos):
        for rect in self.rects:
            if rect.collidepoint(pos):
                return rect

    def _update_touching(self, rect):
        self.touching = list(
            other for other in self.rects
            if other is not rect
            and pygamelib.touch_relation(rect, other)
        )

    def do_mousemotion(self, event):
        rect = self._find_rect(event.pos)
        if rect:
            self.hovering = rect
            self._update_touching(rect)
        else:
            self.hovering = None
            self.touching.clear()
        self.draw()

    def _toggle_selected(self, rect):
        if rect in self.selected:
            self.selected.remove(rect)
        else:
            self.selected.append(rect)

    def do_mousebuttondown(self, event):
        rect = self._find_rect(event.pos)
        if rect:
            self._toggle_selected(rect)

    def update(self):
        super().update()
        keys = pygame.key.get_pressed()
        dx = -keys[pygame.K_LEFT] + keys[pygame.K_RIGHT]
        dy = -keys[pygame.K_UP] + keys[pygame.K_DOWN]
        for rect in self.selected:
            rect.x += dx
            rect.y += dy
        self.draw()

    def draw(self):
        self.screen.fill('black')
        for i, rect in enumerate(self.rects):
            if rect in self.touching or rect is self.hovering:
                width = 0 # fill
            else:
                width = 1
            color = 'orange' if rect is self.hovering else 'darkorange4'
            pygame.draw.rect(self.screen, color, rect, width)

            if rect in self.selected:
                pygame.draw.rect(self.screen, 'magenta', rect, 1)

            side_values = pygamelib.extremities(rect)
            attrs = ('midtop', 'midright', 'midbottom', 'midleft')
            for value, attr in zip(side_values, attrs):
                image = self.printer([str(value)])
                attrvalue = getattr(pygame.Rect(rect), attr)
                _rect = image.get_rect(**{attr: attrvalue})
                self.screen.blit(image, _rect)
            image = self.printer([f'{i=}'])
            self.screen.blit(image, image.get_rect(center=center(rect)))
        pygame.display.flip()


def center(rect):
    x, y, w, h = rect
    return (x + w / 2, y + h / 2)

def main(argv=None):
    """
    Find islands of rects. Highlight rect under cursor and other rects that
    directly touch it.
    """
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'rects',
        type = argparse.FileType('rb'),
        help = 'Pickle file list of rects.',
    )
    args = parser.parse_args(argv)
    rects = list(map(pygame.Rect, pickle.load(args.rects)))
    font = pygamelib.monospace_font(15)
    printer = pygamelib.FontPrinter(font, 'white')
    state = Touches(rects, font, printer)
    engine = pygamelib.Engine()
    pygame.display.set_mode(args.display_size)
    engine.run(state)

if __name__ == '__main__':
    main()

# 2024-02-06 Tue.
# - find rects that touch
# - group rects into "islands" where there is a path to every other rect by way
#   of their touching sides
# - motivation: pygamelib.generate_contiguous is broken, it returns results for
#   rects that are not touching
# 2024-03-19 Tue.
# - revisiting
# - generate_contiguous seems to work now
# - the rects cannot overlap or even share a border
# - the difference between left and right, say, must be zero rather than zero,
#   negative or greater than zero.
# - thinking of making a border relationship generator
#   - the right side of one rect against all the left sides of all other rects
#   - use the tuple interface for rects instead of pygame.Rect
# 2024-03-19 Tue. 11:58 PM
# - load from pickle and convert to pygame.Rect
# - allow moving selected rects with keys
