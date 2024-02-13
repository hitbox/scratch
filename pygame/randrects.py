import argparse
import random

import pygamelib

def random_rect(xrange, yrange, widthrange, heightrange):
    x = random.randint(*xrange)
    y = random.randint(*yrange)
    w = random.randint(*widthrange)
    h = random.randint(*heightrange)
    return (x, y, w, h)

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n',
        type = int,
        default = '10',
        help = 'Number of random rects.',
    )
    parser.add_argument(
        '--xrange',
        type = pygamelib.sizetype(),
        default = '0,100',
    )
    parser.add_argument(
        '--yrange',
        type = pygamelib.sizetype(),
        default = '0,100',
    )
    parser.add_argument(
        '--wrange',
        type = pygamelib.sizetype(),
        default = '10,100',
        help = 'Range of widths',
    )
    parser.add_argument(
        '--hrange',
        type = pygamelib.sizetype(),
        default = '10,100',
        help = 'Range of heights',
    )
    pygamelib.add_null_separator_flag(parser)
    pygamelib.add_rect_dimension_separator_option(parser)
    return parser

def main(argv=None):
    """
    Generate random, zero-positioned rects.
    """
    parser = argument_parser()
    args = parser.parse_args(argv)
    null_separator = vars(args)['0']

    rects = [random_rect(args.xrange, args.yrange, args.wrange, args.hrange)
             for _ in range(args.n)]

    rect_string = pygamelib.format_pipe(rects, null_separator, args.dimsep)
    pygamelib.print_pipe(rect_string, null_separator)

if __name__ == '__main__':
    main()
