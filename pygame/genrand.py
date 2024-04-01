import argparse
import random
import string

import pygamelib

class GibberishWords:

    def __init__(self, min_len, max_len):
        self.min_len = min_len
        self.max_len = max_len

    @classmethod
    def from_args(cls, args):
        return cls(args.min_len, args.max_len)

    def __call__(self):
        n = random.randint(self.min_len, self.max_len)
        letters = random.sample(string.ascii_lowercase, n)
        return ''.join(letters).title()


class RandomCircleFromRange:

    def __init__(self, xrange, yrange, radiusrange):
        self.xrange = xrange
        self.yrange = yrange
        self.radiusrange = radiusrange

    @staticmethod
    def add_parser_options(parser):
        _add_xy_range_arguments(parser)
        parser.add_argument(
            '--radiusrange',
            type = pygamelib.sizetype(),
            default = '0,100',
            help = 'Range for random radius values. Default: %(default)s.',
        )

    @classmethod
    def from_args(cls, args):
        return cls(args.xrange, args.yrange, args.radiusrange)

    def __call__(self):
        x = random.randint(*self.xrange)
        y = random.randint(*self.yrange)
        r = random.randint(*self.radiusrange)
        return (x, y, r)


class RandomRectFromRanges:

    def __init__(self, xrange, yrange, wrange, hrange):
        self.xrange = xrange
        self.yrange = yrange
        self.wrange = wrange
        self.hrange = hrange

    @staticmethod
    def add_parser_options(parser):
        _add_xy_range_arguments(parser)
        parser.add_argument(
            '--wrange',
            type = pygamelib.sizetype(),
            default = _default_range(),
            help = 'Range for random widths. Default: %(default)s',
        )
        parser.add_argument(
            '--hrange',
            type = pygamelib.sizetype(),
            default = _default_range(),
            help = 'Range for random heights. Default: %(default)s',
        )

    @classmethod
    def from_args(cls, args):
        return cls(args.xrange, args.yrange, args.wrange, args.hrange)

    def __call__(self):
        x = random.randint(*self.xrange)
        y = random.randint(*self.yrange)
        w = random.randint(*self.wrange)
        h = random.randint(*self.hrange)
        return (x, y, w, h)


class RandomRectFromPoints:

    def __init__(
        self,
        domain,
        overlap_to_touching = False,
    ):
        self.domain = domain
        # TODO: overlap_to_touching
        self.overlap_to_touching = overlap_to_touching
        if self.overlap_to_touching:
            raise NotImplementedError

    @classmethod
    def from_args(cls, args):
        return cls(args.domain, args.overlap_to_touching)

    def __call__(self):
        left, top, right, bottom = self.domain
        while True:
            x1, x2 = sorted(random.randint(left, right) for _ in range(2))
            y1, y2 = sorted(random.randint(left, right) for _ in range(2))
            w = x2 - x1
            h = y2 - y1
            if w > 0 and h > 0:
                break
        return (x1, y1, w, h)


def _default_range():
    half = min(pygamelib.DEFAULT_DISPLAY_SIZE) // 2
    return f'0,{half}'

def _add_xy_range_arguments(sp, **kwargs):
    default = kwargs.setdefault('default', _default_range())
    type = kwargs.setdefault('type', pygamelib.sizetype())
    # TODO
    # - handle ranges with negative integers
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

def add_options_for_output(parser):
    pygamelib.add_null_separator_flag(
        parser,
        help = 'Separate rects with null.',
    )
    pygamelib.add_dimension_separator_option(
        parser,
        help = 'Rect dimensions separator.',
    )
    pygamelib.add_seed_option(parser)

def add_circle_subparser(subparsers, cmdname):
    """
    add random circle subcommand
    """
    sp = subparsers.add_parser(cmdname)
    pygamelib.add_number_option(
        sp,
        help = 'Number of circles to generate. Default: %(default)s.',
    )
    RandomCircleFromRange.add_parser_options(sp)
    add_options_for_output(sp)
    sp.set_defaults(make_generator=RandomCircleFromRange.from_args)

def add_rects_from_ranges(subparsers, cmdname):
    sp = subparsers.add_parser(
        cmdname,
        help = 'Random rects from ranges for x, y, width, and height.',
    )
    pygamelib.add_number_option(
        sp,
        help = 'Number of rects to generate. Default: %(default)s.',
    )
    RandomRectFromRanges.add_parser_options(sp)
    add_options_for_output(sp)
    sp.set_defaults(make_generator=RandomRectFromRanges.from_args)

def domain_type(string):
    left, top, right, bottom = map(int, string.replace(',', ' ').split())
    return (left, top, right, bottom)

def add_rects_from_points_subparser(subparsers, cmdname):
    sp = subparsers.add_parser(
        cmdname,
        help = 'Random rects from two points in a domain.',
    )
    sp.add_argument(
        'domain',
        type = domain_type,
        help = 'left, top, right, bottom. commas optional.',
    )
    pygamelib.add_number_option(
        sp,
        help = 'Number of rects to generate. Default: %(default)s.',
    )
    sp.add_argument(
        '--overlap-to-touching',
        default = False,
        help = 'Resolve random rects to touching if they overlap.',
    )
    pygamelib.add_dimension_separator_option(
        sp,
        help = 'Rect dimensions separator.',
    )
    pygamelib.add_null_separator_flag(
        sp,
        help = 'Separate rects with null.',
    )
    pygamelib.add_seed_option(sp)
    sp.set_defaults(make_generator=RandomRectFromPoints.from_args)

def add_gibberish_words_subparser(subparsers, cmdname):
    sp = subparsers.add_parser(
        cmdname,
        help = 'Random gibberish words.',
    )
    pygamelib.add_number_option(
        sp,
        help = 'Number of words to generate. Default: %(default)s.',
    )
    pygamelib.add_null_separator_flag(
        sp,
        help = 'Separate words with null.',
    )
    sp.add_argument(
        '--min_len',
        type = int,
        default = 1,
        help = 'Minimum random word length. Default: %(default)s.',
    )
    sp.add_argument(
        '--max_len',
        type = int,
        default = 8,
        help = 'Maximum random word length. Default: %(default)s.',
    )
    # TODO
    # - dimensions separator is nonsense for this subparser!
    pygamelib.add_dimension_separator_option(
        sp,
        default = '',
        help = 'Nonsense!',
    )
    pygamelib.add_seed_option(sp)
    sp.set_defaults(make_generator=GibberishWords.from_args)

def main(argv=None):
    """
    Generate random, zero-positioned rects.
    """
    parser = argparse.ArgumentParser(
        description = 'Randomly generate shapes.',
    )
    subparsers = parser.add_subparsers(
        help = 'Type of shape.',
        required = True,
    )
    add_circle_subparser(subparsers, 'circles-from-ranges')
    add_rects_from_ranges(subparsers, 'rects-from-ranges')
    add_rects_from_points_subparser(subparsers, 'rects-from-points')
    add_gibberish_words_subparser(subparsers, 'gibberish-words')
    # TODO
    # - loop over all subparsers adding the options that are pretty much
    #   required here
    args = parser.parse_args(argv)

    if args.seed:
        random.seed(args.seed)

    null_separator = args.null
    generator = args.make_generator(args)
    items = [generator() for _ in range(args.n)]

    string = pygamelib.format_pipe(items, null_separator, args.dimsep)
    pygamelib.print_pipe(string, null_separator)

if __name__ == '__main__':
    main()
