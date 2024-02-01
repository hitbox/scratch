import argparse
import random

import pygamelib

def random_size(minwidth, minheight, maxwidth, maxheight):
    width = random.randint(minwidth, maxwidth)
    height = random.randint(minheight, maxheight)
    return (width, height)

def generate_rects(n, minsize, maxsize):
    minwidth, minheight = minsize
    maxwidth, maxheight = maxsize

    def _randrect():
        return random_size(minwidth, minheight, maxwidth, maxheight)

    for _ in range(n):
        yield (0, 0, *_randrect())

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n',
        type = int,
        default = '10',
        help = 'Number of random rects.',
    )
    parser.add_argument(
        '--minsize',
        type = pygamelib.sizetype(),
        default = '50',
        help = 'Minimum rect size.',
    )
    parser.add_argument(
        '--maxsize',
        type = pygamelib.sizetype(),
        default = '100',
        help = 'Maximum rect size.',
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

    # validate size values
    if not all(val > 0 for val in args.minsize):
        parser.error('min must be greater than zero')

    if not all(val > 0 for val in args.maxsize):
        parser.error('max must be greater than zero')

    # validate sizes in relation to each other
    minwidth, minheight = args.minsize
    maxwidth, maxheight = args.maxsize

    if minwidth > maxwidth:
        parser.error('min width greater than max')

    if minheight > maxheight:
        parser.error('min height greater than max')

    rects = generate_rects(args.n, args.minsize, args.maxsize)
    null_separator = vars(args)['0']

    rect_string = pygamelib.format_pipe(rects, null_separator, args.dimsep)
    pygamelib.print_pipe(rect_string, null_separator)

if __name__ == '__main__':
    main()
