import argparse
import random

class Rect:

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __repr__(self):
        return f'{self.__class__.__name__}(x={self.x}, y={self.y}, w={self.w}, h={self.h})'

    @classmethod
    def random_size(cls, max_width, max_height, min_width=1, min_height=1):
        return cls(
            x = 0,
            y = 0,
            w = random.randint(min_width, max_width),
            h = random.randint(min_height, max_height),
        )


def generate_random_rects(n, max_width, max_height):
    for _ in range(n):
        yield Rect.random_size(max_width, max_height)

def generate_random_rects_from_args(args):
    n = args.random
    max_width = args.random_max_width
    max_height = args.random_max_height
    rects_generator = generate_random_rects(n, max_width, max_height)
    return rects_generator

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--random',
        type = int,
        metavar = 'N',
        # TODO: read file from file
        required = True,
        help = 'Pack randomly generated %(metavar)s rects.',
    )
    parser.add_argument(
        '--random-seed',
        type = int,
        metavar = 'a',
        help = 'random.seed(%(metavar)s).',
    )
    parser.add_argument(
        '--random-max-width',
        metavar = 'W',
        default = 10,
        help = 'Max random width %(metavar)s. Default: %(default)s',
    )
    parser.add_argument(
        '--random-max-height',
        metavar = 'H',
        default = 10,
        help = 'Max random height %(metavar)s. Default: %(default)s',
    )
    args = parser.parse_args(argv)

    if isinstance(args.random_seed, int):
        random.seed(args.random_seed)

    rects = list(generate_random_rects_from_args(args))
    from pprint import pprint
    pprint(rects)

if __name__ == '__main__':
    main()

# 2024-08-11 Sun.
# - Reading this:
#   https://chevyray.dev/blog/creating-175-fonts/
# - Mentions this rect packer:
#   https://github.com/ChevyRay/crunch-rs
# - Felt like starting my own rect packer.
