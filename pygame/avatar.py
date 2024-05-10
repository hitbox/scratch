import argparse
import io
import itertools as it
import random
import sys

import pygamelib

from pygamelib import pygame

def main(argv=None):
    """
    Generate a random avatar with an eye towards making random favicons for web
    apps.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--size',
        type = pygamelib.sizetype(),
        default = '4',
        help = 'Size of image. Default: %(default)s.',
    )
    pygamelib.add_seed_option(parser)
    args = parser.parse_args(argv)

    if args.seed:
        random.seed(args.seed)

    avatar = pygame.Surface(args.size)
    rect = avatar.get_rect()

    for pos in it.product(*map(range, rect.size)):
        if random.choice([0,1]):
            avatar.set_at(pos, 'white')

    with io.BytesIO() as output:
        pygame.image.save(avatar, output, 'png')
        sys.stdout.buffer.write(output.getvalue())

if __name__ == '__main__':
    main()
