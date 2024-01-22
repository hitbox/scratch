import argparse

from lib.types import inttup

def simple_parser(**kwargs):
    parser = argparse.ArgumentParser(**kwargs)
    parser.add_argument(
        '--screen-size',
        type=inttup,
        help='Two-tuple comma separated screen size.')
    parser.add_argument('--framerate', type=int)
    return parser
