import argparse
import math

from pprint import pprint

import pygamelib

from pygamelib import pygame

from pygame.color import THECOLORS

class ColorGrid(pygamelib.DemoBase):

    def __init__(self, drawables):
        self.drawables = drawables
        self.offset = pygame.Vector2()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()

    def do_mousemotion(self, event):
        if event.buttons[0]:
            self.offset += event.rel
            pygamelib.post_videoexpose()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        for image, rect in self.drawables:
            x, y, *_ = rect
            self.screen.blit(image, self.offset + (x, y))
        pygame.display.flip()


def render_swatch(font, size, background, color, name):
    result_image = pygame.Surface(size)
    result_image.fill(background)
    result_rect = result_image.get_rect()
    label_background = pygame.Color(background).lerp('black', 0.5)
    text_image = font.render(name, True, color, label_background)
    text_rect = text_image.get_rect(center=result_rect.center)
    result_image.blit(text_image, text_rect)
    return result_image

def _arrange(rects, ncols):
    # needed to pull the arrange_columns function apart to add gaps and resize
    # the arranged rects
    rows, cols = pygamelib.groupby_columns(rects, ncols)
    row_wraps, col_wraps = pygamelib.rowcolwraps(rows, cols)

    for rowwrap in row_wraps:
        rowwrap.height *= 4

    for colwrap in col_wraps:
        colwrap.width *= 1.10

    pygamelib.flow_topbottom(row_wraps, 20)
    pygamelib.flow_leftright(col_wraps, 20)

    for rowwrap, _rects in zip(row_wraps, rows, strict=True):
        for rect in _rects:
            rect.height = rowwrap.height
            rect.centery = rowwrap.centery

    for colwrap, _rects in zip(col_wraps, cols, strict=True):
        for rect in _rects:
            rect.width = colwrap.width
            rect.left = colwrap.left

def run(display_size, colors, names, font_size, colortext):
    assert len(colors) == len(names)
    pygame.font.init()
    font = pygame.font.SysFont('monospace', font_size)

    rects = [pygame.Rect((0,)*2, font.size(name)) for name in names]
    ncols = math.isqrt(len(rects)) // 2
    _arrange(rects, ncols)

    images = [render_swatch(font, rect.size, color, 'white', name) for rect, color, name in zip(rects, colors, names)]

    drawables = list(zip(images, rects))
    demo = ColorGrid(drawables)
    engine = pygamelib.Engine()

    pygame.display.set_mode(display_size)
    engine.run(demo)

def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--screen-size',
        type = pygamelib.sizetype(),
        default = '1000',
    )
    parser.add_argument(
        '--font-size',
        type = int,
        default = '15',
    )
    parser.add_argument('--print', action='store_true')
    parser.add_argument('--filter')
    parser.add_argument('--sort')
    parser.add_argument('--text')
    args = parser.parse_args(argv)
    return args

def main():
    args = parse_args()

    sort_expr = compile(args.sort, '<sort>', 'eval')
    filter_expr = compile(args.filter, '<filter>', 'eval')

    def predicate(color):
        return eval(filter_expr, {'color': color})

    def sort_key(color):
        return eval(sort_expr, {'color': color})

    colors = map(pygame.Color, THECOLORS.values())
    colors = sorted(filter(predicate, colors), key=sort_key)
    colortext = str
    names = list(map(pygamelib.color_name, colors))
    if args.print:
        pprint(names)
    run(args.screen_size, colors, names, args.font_size, colortext)

if __name__ == '__main__':
    main()
