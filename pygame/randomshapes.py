import argparse
import random

import pygamelib

def random_point(args):
    x = random.randint(*args.xrange)
    y = random.randint(*args.yrange)
    return (x, y)

def random_circle(args):
    x, y = random_point(args)
    r = random.randint(*args.radiusrange)
    return (x, y, r)

def random_rect(args):
    x, y = random_point(args)
    w = random.randint(*args.wrange)
    h = random.randint(*args.hrange)
    return (x, y, w, h)

def _add_xy_range_arguments(sp, **kwargs):
    default = kwargs.setdefault('default', '0,100')
    type = kwargs.setdefault('type', pygamelib.sizetype())
    sp.add_argument(
        '--xrange',
        type = type,
        default = default,
        help = 'Range for random x values. Default: %(default)s.',
    )
    sp.add_argument(
        '--yrange',
        type = type,
        default = default,
        help = 'Range for random y values. Default: %(default)s.',
    )

def add_number_option(parser, name='-n', **kwargs):
    kwargs.setdefault('type', int)
    kwargs.setdefault('default', 1)
    parser.add_argument(name, **kwargs)

def _add_number_option(parser):
    add_number_option(
        parser,
        help = 'Number of random shapes. Default: %(default)s',
    )

def add_circle_subparser(subparsers):
    """
    add random circle subcommand
    """
    sp = subparsers.add_parser('circle')
    _add_number_option(sp)
    _add_xy_range_arguments(sp)
    sp.add_argument(
        '--radiusrange',
        type = pygamelib.sizetype(),
        default = '0,100',
        help = 'Range for random radius values. Default: %(default)s.',
    )
    pygamelib.add_null_separator_flag(
        sp,
        help  = 'Separate circles with null.',
    )
    pygamelib.add_dimension_separator_option(
        sp,
        help = 'Circle dimensions separator.',
    )
    sp.set_defaults(random_func=random_circle)

def add_rect_subparser(subparsers):
    """
    add random rect subcommand
    """
    sp = subparsers.add_parser('rect')
    _add_number_option(sp)
    _add_xy_range_arguments(sp)
    sp.add_argument(
        '--wrange',
        type = pygamelib.sizetype(),
        default = '10,100',
        help = 'Range for random widths. Default: %(default)s',
    )
    sp.add_argument(
        '--hrange',
        type = pygamelib.sizetype(),
        default = '10,100',
        help = 'Range for random heights. Default: %(default)s',
    )
    pygamelib.add_null_separator_flag(
        sp,
        help = 'Separate rects with null.',
    )
    pygamelib.add_dimension_separator_option(
        sp,
        help = 'Rect dimensions separator.',
    )
    sp.set_defaults(random_func=random_rect)

def argument_parser():
    parser = argparse.ArgumentParser(
        description = 'Randomly generate shapes.',
    )

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
