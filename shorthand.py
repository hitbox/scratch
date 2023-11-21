import argparse
import unittest

class TestShorthand(unittest.TestCase):

    def check_shorthand_args(self, input_, output):
        result = list(shorthand(*input_))
        self.assertEqual(list(output), result)

    def check_shorthand_kwargs(self, inputdict, output):
        result = list(shorthand(**inputdict))
        self.assertEqual(list(output), result)

    def test_shorthand_one(self):
        self.check_shorthand_args([1], [1,1,1,1])

    def test_shorthand_two(self):
        self.check_shorthand_args([1,2], [1,2,1,2])

    def test_shorthand_three(self):
        self.check_shorthand_args([1,2,3], [1,2,3,2])

    def test_shorthand_four(self):
        self.check_shorthand_args([1,2,3,4], [1,2,3,4])

    def test_shorthand_one_kw(self):
        self.check_shorthand_kwargs(dict(top=3), [3,3,3,3])

    def test_shorthand_two_kw(self):
        kw = dict(top=3, right=4)
        self.check_shorthand_kwargs(kw, [3,4,3,4])

    def test_shorthand_three_kw(self):
        kw = dict(top=3, right=4, bottom=1)
        self.check_shorthand_kwargs(kw, [3,4,1,4])

    def test_shorthand_four_kw(self):
        kw = dict(top=3, right=4, bottom=1, left=2)
        self.check_shorthand_kwargs(kw, [3,4,1,2])

    def test_shorthand_mixed(self):
        result = list(shorthand(1, right=2))
        self.assertEqual([1,2,1,2], result)
        result = list(shorthand(1, 2, bottom=3))
        self.assertEqual([1,2,3,2], result)

    def test_shorthand_raise_for_empty(self):
        self.assertRaises(AssertionError, shorthand)

    def test_shorthand_raise_for_duplicate(self):
        self.assertRaises(AssertionError, shorthand, 2, top=1)


def shorthand(*args, **kwargs):
    """
    Expand argument like CSS shorthand properties.
    """
    assert args or kwargs
    sides = 'top right bottom left'.split()
    sidesdict = dict(zip(sides, args))
    assert not set(sidesdict).intersection(kwargs)
    sidesdict.update(kwargs)
    sidesdict.setdefault('right', sidesdict['top'])
    sidesdict.setdefault('left', sidesdict['right'])
    sidesdict.setdefault('bottom', sidesdict['top'])
    return [sidesdict[key] for key in sides]

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('values', nargs='+')
    args = parser.parse_args(argv)
    props = list(shorthand(*args.values))
    print(' '.join(props))

if __name__ == '__main__':
    main()

# 2023-10-08
# - pulled out of old code: rect-editor/rectedit.py
#   https://developer.mozilla.org/en-US/docs/Web/CSS/Shorthand_properties
