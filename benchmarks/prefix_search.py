import abc
import argparse
import functools
import timeit
import unittest

from bisect import bisect_left

class TestPrefixSearchBase(abc.ABC):
    # sorted list of words
    words = ['another', 'data', 'date', 'hello', 'text', 'word']

    @property
    @abc.abstractmethod
    def prefix_search_func(self):
        ...

    def check_prefix(self, prefix, expect):
        result = list(self.prefix_search_func(self.words, prefix))
        self.assertEqual(expect, result)

    def test_prefix_search(self):
        self.check_prefix('dat', ['data', 'date'])

    def test_prefix_search_none(self):
        self.check_prefix('zip', [])

    def test_prefix_search_first(self):
        self.check_prefix('ano', ['another'])

    def test_prefix_search_last(self):
        self.check_prefix('wo', ['word'])


class TestPrefixSearchLoopFlavor1(unittest.TestCase, TestPrefixSearchBase):

    @functools.cached_property
    def prefix_search_func(self):
        return prefix_search_loop_flavor1


class TestPrefixSearchLoopFlavor2(unittest.TestCase, TestPrefixSearchBase):

    @functools.cached_property
    def prefix_search_func(self):
        return prefix_search_loop_flavor2


class TestPrefixSearchLoopFlavor3(unittest.TestCase, TestPrefixSearchBase):

    @functools.cached_property
    def prefix_search_func(self):
        return prefix_search_loop_flavor3


class TestPrefixSearchBisect(unittest.TestCase, TestPrefixSearchBase):

    @functools.cached_property
    def prefix_search_func(self):
        return prefix_search_bisect


def prefix_search_loop_flavor1(wordlist, prefix):
    # nested loops on iterator
    words = iter(wordlist)
    for word in words:
        if word.startswith(prefix):
            yield word
            for word in words:
                if not word.startswith(prefix):
                    break
                yield word

def prefix_search_loop_flavor2(wordlist, prefix):
    # un-nested loops on iterator
    words = iter(wordlist)
    for word in words:
        if word.startswith(prefix):
            yield word
            break
    for word in words:
        if not word.startswith(prefix):
            break
        yield word

def prefix_search_loop_flavor3(wordlist, prefix):
    # a switch used to break without iterator
    found = 0
    for word in wordlist:
        if word.startswith(prefix):
            yield word
            if not found:
                found += 1
        elif found:
            # does not start with and we've already found one
            break

def prefix_search_bisect(wordlist, prefix):
    try:
        index = bisect_left(wordlist, prefix)
    except IndexError:
        pass
    else:
        while index < len(wordlist) and wordlist[index].startswith(prefix):
            yield wordlist[index]
            index += 1

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix_and_words', nargs='+')
    parser.add_argument('--func', choices=['loop', 'bisect'], default='loop')
    args = parser.parse_args(argv)

    if len(args.prefix_and_words) < 2:
        parser.error('two or more arguments are required')

    prefix, *wordlist = args.prefix_and_words

    if args.func == 'loop':
        func = prefix_search_loop
    elif args.func == 'bisect':
        func = prefix_search_bisect

    print(func.__name__)
    for word in func(wordlist, prefix):
        print(word)

if __name__ == '__main__':
    main()

# https://martinheinz.dev/blog/106
