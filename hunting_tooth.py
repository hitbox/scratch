import argparse

from itertools import cycle
from itertools import zip_longest
from math import gcd as greatest_common_denominator

def main(argv=None):
    """
    Dicking around because I heard about hunting tooth gears on a helicopter
    video by "bzig".
    https://www.youtube.com/watch?v=7UUHPdK0YYI
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('gears', nargs='+', type=int)
    args = parser.parse_args(argv)

    gear1, gear2 = sorted(args.gears)
    ratio = gear1 / gear2

    gcd = greatest_common_denominator(*args.gears)
    if gcd > 1:
        print(f'Non-hunting tooth gears {gcd=}')

    num_teeth1 = cycle(range(gear1))
    num_teeth2 = cycle(range(gear2))

    revolution = 0
    while revolution < 3:
        tooth1 = next(num_teeth1)
        tooth2 = next(num_teeth2)
        print(f'{revolution=}, {tooth1=}, {tooth2=}')
        if tooth1 == 0:
            revolution += 1

if __name__ == '__main__':
    main()
