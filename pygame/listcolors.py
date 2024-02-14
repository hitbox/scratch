import argparse
import itertools as it
import math
import operator as op
import os
import string
import textwrap

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
            self.draw()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        for image, rect in self.drawables:
            x, y, *_ = rect
            self.screen.blit(image, self.offset + (x, y))
        pygame.display.flip()


def _arrange(rects, ncols):
    # needed to pull the arrange_columns function apart to add gaps and resize
    # the arranged rects
    table = list(pygamelib.batched(rects, ncols))

    row_wraps = list(map(pygame.Rect, map(pygamelib.wrap, table)))
    col_wraps = it.zip_longest(*table, fillvalue=pygamelib.NORECT)
    col_wraps = list(map(pygame.Rect, map(pygamelib.wrap, col_wraps)))

    # add some width and height padding
    for rowwrap in row_wraps:
        rowwrap.height *= 4

    for colwrap in col_wraps:
        colwrap.width *= 1.10

    # end-to-end flow rows and columns
    pygamelib.flow_leftright(col_wraps, 20)
    pygamelib.flow_topbottom(row_wraps, 20)

    # align rects inside rows and columns
    for rowwrap, _rects in zip(row_wraps, table, strict=True):
        for rect in _rects:
            rect.height = rowwrap.height
            rect.centery = rowwrap.centery

    for colwrap, _rects in zip(col_wraps, it.zip_longest(*table)):
        for rect in _rects:
            if rect:
                rect.width = colwrap.width
                rect.left = colwrap.left

def run(display_size, colors, names, font_size, colortext, predicate, sortkey):
    assert len(colors) == len(names)
    font = pygamelib.monospace_font(font_size)

    rects = [pygame.Rect((0,)*2, font.size(name)) for name in names]
    ncols = math.isqrt(len(rects))
    _arrange(rects, ncols)

    def text(color, name):
        return name

    images = [pygamelib.render_text(font, rect.size, color, 'white', text(color, name))
              for rect, color, name in zip(rects, colors, names)]

    drawables = list(zip(images, rects))
    demo = ColorGrid(drawables)
    demo.offset = -pygamelib.centered_offset(rects, display_size)

    engine = pygamelib.Engine()

    pygame.display.set_mode(display_size)
    engine.run(demo)

def auto_completion_script():
    # TODO
    # - this is a work in progress
    # - have not discovered how to complete after
    #   something like `python listcolors.py`
    # - would like after `python listcolors.py`<tab><tab> to
    #   show all the options
    filename = os.path.basename(__file__)
    root, ext = os.path.splitext(filename)
    template = textwrap.dedent('''\
    _{root}() {{
        local cur prev opts
        cur="${{COMP_WORDS[COMP_CWORD]}}"
        prev="${{COMP_WORDS[COMP_CWORD-1]}}"
        case "${{prev}}" in
            --filter)
                COMPREPLY=($(compgen -W "test1 test2 test3" -- ${{cur}}))
                ;;
            *)
                COMPREPLY=()
                ;;
        esac
    }}
    # -F function
    complete -F _{root} "python {filename}"
    ''')
    context = globals()
    context.update(ext=ext, filename=filename, root=root)
    return template.format(**context)

def argument_parser():
    parser = argparse.ArgumentParser()
    pygamelib.add_display_size_option(
        parser,
        default = '1900,900',
    )
    parser.add_argument(
        '--auto-completion',
        action = 'store_true',
    )
    parser.add_argument(
        '--font-size',
        type = int,
        default = '15',
    )
    parser.add_argument(
        '--print',
        action = 'store_true',
    )
    parser.add_argument(
        '--filter',
        type = pygamelib.eval_type('filter', 'color'),
        default = 'True', # default to all colors
        help = 'Expression filter function.',
    )
    parser.add_argument(
        '--sort',
        type = pygamelib.eval_type('sort', 'color'),
        # NOTE:
        # - pygame.Color do not have __lt__
        default = 'tuple(color)', # default to (r, g, b, a) sort
        help = 'Expression for sort key.',
    )
    parser.add_argument(
        '--text',
        type = pygamelib.eval_type('text', 'color'),
        default = 'str',
        help = 'Expression for color labels.',
    )
    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)
    if args.auto_completion:
        print(auto_completion_script())
        return
    colors = pygamelib.UNIQUE_THECOLORS.values()
    colors = map(pygamelib.ColorAttributes, colors)
    colors = sorted(filter(args.filter, colors), key=args.sort)
    names = list(map(pygamelib.color_name, colors))
    if args.print:
        pprint(names)
    run(args.display_size, colors, names, args.font_size, args.text, args.filter, args.sort)

if __name__ == '__main__':
    main()
