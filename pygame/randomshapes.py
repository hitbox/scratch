import argparse
import random

import pygamelib

def random_circle(args):
    x = random.randint(*args.xrange)
    y = random.randint(*args.yrange)
    r = random.randint(*args.radiusrange)
    return (x, y, r)

def random_rect(args):
    x = random.randint(*args.xrange)
    y = random.randint(*args.yrange)
    w = random.randint(*args.wrange)
    h = random.randint(*args.hrange)
    return (x, y, w, h)

def add_circle_subparser(subparsers):
    """
    add random circle subcommand
    """
    sp = subparsers.add_parser('circle')
    sp.add_argument(
        '--xrange',
        type = pygamelib.sizetype(),
        default = '0,100',
    )
    sp.add_argument(
        '--yrange',
        type = pygamelib.sizetype(),
        default = '0,100',
    )
    sp.add_argument(
        '--radiusrange',
        type = pygamelib.sizetype(),
        default = '0,100',
    )
    sp.set_defaults(random_func=random_circle)

def add_rect_subparser(subparsers):
    """
    add random rect subcommand
    """
    sp = subparsers.add_parser('rect')
    sp.add_argument(
        '--xrange',
        type = pygamelib.sizetype(),
        default = '0,100',
    )
    sp.add_argument(
        '--yrange',
        type = pygamelib.sizetype(),
        default = '0,100',
    )
    sp.add_argument(
        '--wrange',
        type = pygamelib.sizetype(),
        default = '10,100',
        help = 'Range of widths',
    )
    sp.add_argument(
        '--hrange',
        type = pygamelib.sizetype(),
        default = '10,100',
        help = 'Range of heights',
    )
    sp.set_defaults(random_func=random_rect)

def add_number_option(parser, name='-n', **kwargs):
    kwargs.setdefault('type', int)
    kwargs.setdefault('default', 0)
    parser.add_argument(name, **kwargs)

def argument_parser():
    parser = argparse.ArgumentParser()
    add_number_option(parser, help='Number of random shapes. Default: %(default)s')
    pygamelib.add_null_separator_flag(parser)
    pygamelib.add_dimension_separator_option(parser)

    subparsers = parser.add_subparsers(help='Type of shape.')
    add_circle_subparser(subparsers)
    add_rect_subparser(subparsers)

    return parser

def main(argv=None):
    """
    Generate random, zero-positioned rects.
    """
    parser = argument_parser()
    args = parser.parse_args(argv)
    null_separator = vars(args)['0']

    shapes = [args.random_func(args) for _ in range(args.n)]
    string = pygamelib.format_pipe(shapes, null_separator, args.dimsep)
    pygamelib.print_pipe(string, null_separator)

if __name__ == '__main__':
    main()
