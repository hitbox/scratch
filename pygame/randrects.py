import argparse
import random

import pygamelib

def randrect(minwidth, minheight, maxwidth, maxheight):
    width = random.randint(minwidth, maxwidth)
    height = random.randint(minheight, maxheight)
    return (width, height)

def main(argv=None):
    """
    Generate random rect args.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default='10')
    parser.add_argument('--minsize', type=pygamelib.sizetype(), default='50')
    parser.add_argument('--maxsize', type=pygamelib.sizetype(), default='100')
    parser.add_argument('-0', action='store_true')
    args = parser.parse_args(argv)

    if not all(val > 0 for val in args.minsize):
        parser.error('min must be greater than zero')

    if not all(val > 0 for val in args.maxsize):
        parser.error('max must be greater than zero')

    minwidth, minheight = args.minsize
    maxwidth, maxheight = args.maxsize

    if minwidth > maxwidth:
        parser.error('min width greater than max')

    if minheight > maxheight:
        parser.error('min height greater than max')

    if vars(args)['0']:
        end = '\0'
    else:
        end = '\n'

    def _randrect():
        return randrect(minwidth, minheight, maxwidth, maxheight)

    sizes = [(0, 0, *_randrect()) for _ in range(args.n)]

    print(end.join(' '.join(map(str, size)) for size in sizes), end='')

if __name__ == '__main__':
    main()
