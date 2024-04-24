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

class ColorGridDemo(
    pygamelib.DemoBase,
    pygamelib.QuitKeydownMixin,
    pygamelib.StopMixin,
):

    def __init__(self, drawables, background_color):
        self.drawables = drawables
        self.background_color = background_color
        self.offset = pygame.Vector2()

    def do_mousemotion(self, event):
        if event.buttons[0]:
            self.offset += event.rel
            self.draw()

    def do_videoexpose(self, event):
        self.draw()

    def _drawables(self):
        for image, rect in self.drawables:
            yield (image, rect.move(*self.offset))

    def draw(self):
        self.screen.fill(self.background_color)
        self.screen.blits(self._drawables())
        pygame.display.flip()


class ColorCardRenderer:

    def __init__(self, font, text_color, label_margin, antialias=True):
        self.font = font
        self.text_color = text_color
        self.label_margin = label_margin
        self.antialias = antialias

    def make_result(self, size, color):
        result_image = pygame.Surface(size)
        result_image.fill(color)
        return result_image

    def make_label_background(self, text, color, background_color, shade_amount):
        label_size = pygame.Vector2(self.font.size(text))
        label_size += self.label_margin
        label_image = pygame.Surface(label_size)
        # shade the color this card is displaying toward a background color so
        # that the text is readable
        fill_color = pygame.Color(color).lerp(background_color, shade_amount)
        label_image.fill(fill_color)
        return label_image

    def __call__(self, size, color, text, background_color, shade_amount):
        result_image = self.make_result(size, color)
        result_rect = result_image.get_rect()

        label_image = self.make_label_background(
            text,
            color,
            background_color,
            shade_amount,
        )
        label_rect = label_image.get_rect()

        text_image = self.font.render(text, self.antialias, self.text_color)

        label_image.blit(text_image, text_image.get_rect(center=label_rect.center))
        result_image.blit(label_image, label_image.get_rect(center=result_rect.center))
        return result_image


def _arrange(rects, ncols, gap=20):
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
    pygamelib.flow_leftright(col_wraps, gap=gap)
    pygamelib.flow_topbottom(row_wraps, gap=gap)

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

def run(display_size, colors, names, font_size, background_color):
    assert len(colors) == len(names)
    font = pygamelib.monospace_font(font_size)

    rects = [pygame.Rect((0,)*2, font.size(name)) for name in names]
    ncols = math.isqrt(len(rects))
    _arrange(rects, ncols)

    def get_text(color, name):
        return name

    # XXX
    # - relying on big number to make the width of the color card image
    color_card_renderer = ColorCardRenderer(font, 'white', label_margin=(999, 10))

    def render_text(rect, color, name):
        """
        Name of color rendered onto an image of size rect with a black shaded
        background the width of the image.
        """
        return color_card_renderer(
            rect.size,
            color,
            get_text(color, name),
            background_color,
            shade_amount = 0.50,
        )

    images = list(map(render_text, rects, colors, names))
    drawables = list(zip(images, rects))
    demo = ColorGridDemo(drawables, background_color)
    demo.offset = pygamelib.centered_offset(rects, display_size)

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
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        '--auto-completion',
        action = 'store_true',
        help = 'Print autocomplete script for bash.',
    )
    parser.add_argument(
        '--font-size',
        type = int,
        default = '15',
        help = 'Font size. Default: %(default)s.',
    )
    parser.add_argument(
        '--print',
        action = 'store_true',
        help = 'Print the colors and exit.',
    )
    pygamelib.add_null_separator_flag(
        parser,
        help = 'Use null separator with --print.',
    )
    parser.add_argument(
        '--filter',
        type = pygamelib.eval_type('filter', 'color'),
        default = 'True', # default to all colors
        help = 'Expression filter function. Default: %(default)s.',
    )
    parser.add_argument(
        '--sort',
        type = pygamelib.eval_type('sort', 'color'),
        # NOTE:
        # - pygame.Color does not have __lt__
        default = 'tuple(color)',
        help = 'Expression for sort key. Default: %(default)s (RGBA).',
    )
    parser.add_argument(
        '--text',
        type = pygamelib.eval_type('text', 'color'),
        default = 'str',
        help = 'Expression for color labels. Default: %(default)s.',
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
    if not colors:
        parser.error('No colors.')
    names = list(map(pygamelib.color_name, colors))
    if args.print:
        if args.null:
            sep = '\0'
        else:
            sep = '\n'
        pygamelib.print_pipe(sep.join(names), args.null)
        return
    run(args.display_size, colors, names, args.font_size, args.background)

if __name__ == '__main__':
    main()

# 2024-04-23 Tue.
# - Waterfall layout
#   https://webkit.org/blog/15269/help-us-invent-masonry-layouts-for-css-grid-level-3/
