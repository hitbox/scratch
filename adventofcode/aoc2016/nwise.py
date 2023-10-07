import argparse
import logging
from itertools import tee

# finally stumbled on an nwise function that eluded me in Advent 2015.
# extrapolated from day03.threewise

def nwise(iterable, n):
    streams = tee(iterable, n)

    for i, stream in enumerate(reversed(streams)):
        for _ in range(n - i):
            next(stream, None)

    values = zip(*streams)
    for x in values:
        yield x
        for _ in range(n - 1):
            next(values)

def show_and_tell():
    l = list(range(28))
    print(l)
    print(list(nwise(l, 3)))

    print(list(nwise(l, 5)))

def consume(iterable):
    return map(lambda x: x, iterable)

def stress():
    MILLION = 1000 * 1000
    BILLION = MILLION * MILLION
    TRILLION = BILLION * BILLION
    print('n-wise-ing a million number into 100\'s pairs.')
    log = logging.getLogger('stress')
    for paired in nwise(range(MILLION), 100):
        log.debug(paired)

def main():
    """
    Demonstrate an n-wise pairing function.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('--stress-test', action='store_true', help='Test doing a lot of these.')
    parser.add_argument('--debug', action='store_true', help='Show debugging')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.stress_test:
        stress()
    else:
        show_and_tell()

if __name__ == '__main__':
    main()
