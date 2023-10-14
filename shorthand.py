import argparse
import itertools as it
import unittest

class TestShorthand(unittest.TestCase):

    def check_shorthand(self, input_, output):
        self.assertEqual(list(shorthand(input_)), list(output))

    def test_shorthand_one(self):
        self.check_shorthand([1], [1,1,1,1])

    def test_shorthand_two(self):
        self.check_shorthand([1,2], [1,2,1,2])

    @unittest.expectedFailure
    def test_shorthand_three(self):
        self.check_shorthand([1,2,3], [1,2,3,2])

    def test_shorthand_four(self):
        self.check_shorthand([1,2,3,4], [1,2,3,4])


def shorthand(values, n=4):
    return it.islice(it.cycle(values), n)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('values', nargs='+')
    args = parser.parse_args(argv)

    # THINK
    # - exlcude first (or nth) each cycle would mess up the second case.
    # - exclude after len(values) % n might work.

    props = list(shorthand(args.values))

    print(' '.join(props))

if __name__ == '__main__':
    main()

# 2023-10-08
# - pulled out of old code: rect-editor/rectedit.py
#   https://developer.mozilla.org/en-US/docs/Web/CSS/Shorthand_properties
