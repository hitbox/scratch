import argparse
import unittest

from fractions import Fraction

class TestRangeArguments(unittest.TestCase):

    def test_range_args_one(self):
        self.assertEqual(rangeargs(1), (0, 1, 1))
        self.assertEqual(rangeargs(10), (0, 10, 1))

    def test_range_args_two(self):
        self.assertEqual(rangeargs(0, 1), (0, 1, 1))
        self.assertEqual(rangeargs(0, 10), (0, 10, 1))
        self.assertEqual(rangeargs(-10, 10), (-10, 10, 1))

    def test_range_args_three(self):
        self.assertEqual(rangeargs(0, 1, 1), (0, 1, 1))
        self.assertEqual(rangeargs(0, 10, 1), (0, 10, 1))
        self.assertEqual(rangeargs(0, 10, 2), (0, 10, 2))


def mix(a, b, x):
    # numerically stable, less floating point errors
    return a * (1 - x) + b * x

def mix2(a, b, x):
    # does not repeat x and is easier to reason about
    return x * (b - a) + a

def linear(a, b, x):
    # normalize x between a and b.
    return (x - a) / (b - a)

def remap(a, b, c, d, x):
    return mix(c, d, linear(a, b, x))

def remap(a, b, c, d, x):
    return x*(d-c)/(b-a) + c-a*(d-c)/(b-a)

def rangeargs(*args):
    n = len(args)
    assert 1 <= n <= 3
    if n == 3:
        start, stop, step = args
    elif n == 2:
        start, stop, step = args + (1,)
    elif n == 1:
        stop, start, step = args + (0, 1)
    return (start, stop, step)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('mixargs', nargs=3, help='a, b, x')
    args = parser.parse_args(argv)

    a, b, x = map(Fraction, args.mixargs)
    print(f'{mix(a, b, x)=}')

if __name__ == '__main__':
    main()

# 2023-11-24
# - http://blog.pkh.me/p/29-the-most-useful-math-formulas.html
# - I like his argument for naming it "mix."

