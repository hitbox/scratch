import argparse
import unittest

from functools import reduce

class TestCompose(unittest.TestCase):

    def test_compose(self):
        self.assertEqual(compose(square, increment)(3), 16)


class TestPipe(unittest.TestCase):

    def test_pipe(self):
        self.assertEqual(sum(map(pipe(add_2, square), range(1,6))), 135)


class TestCurry(unittest.TestCase):

    def test_curry(self):
        self.assertEqual(curry(add)(1)(2)(3), 6)


def compose(f, g):
    return lambda x: f(g(x))

def pipe_sans_lambda(*functions):
    def _pipe(x):
        result = x
        for func in functions:
            result = func(result)
        return result
    return _pipe

def pipe_with_lambda(*functions):
    return lambda x: reduce(lambda v, f: f(v), functions, x)

pipe = pipe_sans_lambda

def curry(func):
    def curried(*args):
        if len(args) >= func.__code__.co_argcount:
            return func(*args)
        return lambda *nextargs: curried(*(args + nextargs))
    return curried

def add(a, b, c):
    return a + b + c

def increment(x):
    return x + 1

def add_2(x):
    return compose(increment, increment)(x)

def square(x):
    return x * x

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

if __name__ == '__main__':
    main()

# 2023-12-29
# https://chat.openai.com/c/e69c8499-6195-456e-a5ae-5a97f16b9dd2
