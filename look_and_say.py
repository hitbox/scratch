import argparse
import itertools as it
import timeit
import unittest

class TestLookAndSay(unittest.TestCase):

    def check(self, a, b):
        self.assertEqual(look_and_say(a), b)
        self.assertEqual(look_and_say_groupby(a), b)

    def test_one(self):
        self.check('1', '11')

    def test_two(self):
        self.check('11', '21')

    def test_three(self):
        self.check('21', '1211')

    def test_four(self):
        self.check('1211', '111221')

    def test_five(self):
        self.check('111221', '312211')

    def test_six(self):
        self.check('312211', '13112221')

    def test_seven(self):
        self.check('13112221', '1113213211')

    def test_eight(self):
        self.check('1113213211', '31131211131221')

    def test_nine(self):
        self.check('31131211131221', '13211311123113112211')


def look_and_say(text):
    new = ''
    i = 0
    n = len(text)
    while i < n-1:
        j = i + 1
        while j < n and text[i] == text[j]:
            j += 1
        new += str(len(text[i:j])) + text[i]
        i = j
    if i < n:
        new += str(len(text[i:])) + text[i]
    return new

def look_and_say_groupby(text):
    new = ''
    for key, grouper in it.groupby(text):
        new += str(len(list(grouper))) + key
    return new

def argument_parser():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    normal_sp = subparsers.add_parser('go')
    normal_sp.add_argument('start')
    normal_sp.add_argument(
        '--iterations',
        type = int,
        default = 10,
        help = 'Number of iterations.',
    )

    timeit_sp = subparsers.add_parser('timeit')

    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)

    if 'start' in args:
        text = args.start
        print(text)
        for _ in range(args.iterations):
            text = look_and_say(text)
            print(text)
    else:
        raise NotImplementedError
        # benchmark
        def wrap(func, text):
            def wrapped():
                nonlocal text
                for _ in range(10):
                    text = func(text)
                    print(text)
            return wrapped

        number = 1000
        time = timeit.timeit(wrap(look_and_say, '1'), number=number)
        print(time)
        time = timeit.timeit(wrap(look_and_say_groupby, '1'), number=number)
        print(time)

if __name__ == '__main__':
    main()
