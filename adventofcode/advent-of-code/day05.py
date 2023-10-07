#!python2
import os
from collections import Counter
from pprint import pprint as pp
from itertools import *

VOWELS = set('aeiou')

BAD_STRINGS = ['ab', 'cd', 'pq', 'xy']

def has_bad_vowels(s):
    for bs in BAD_STRINGS:
        if bs in s:
            return True
    return False

def get_vowels(s):
    return [ c for c in s if c in VOWELS ]

def consume(s, n):
    """
    consume('abcdefg', 3): [ ('a', 'b', 'c'), ('b', 'c', 'd'), ..., ('e', 'f', 'g')
    """
    r = zip(*[ s[i:] for i in range(n) ])
    return r

def iter_overlapping(s):
    for c1, c2 in consume(s, 2):
        if c1 == c2:
            yield c1 + c2

def isnice1(s):
    if has_bad_vowels(s):
        return False

    if len(get_vowels(s)) < 3:
        return False

    if next(iter_overlapping(s), None) is None:
        return False

    return True

def pair_iter(s):
    for i, pair in enumerate(starmap(lambda a,b: a+b, izip(s[:-1], s[1:]))):
        if pair in s[i+2:]:
            yield pair

def at_least_two_pair(s):
    # It contains a pair of any two letters that appears at least twice in the
    # string without overlapping, like xyxy (xy) or aabcdefgaa (aa), but not
    # like aaa (aa, but it overlaps).
    return next(pair_iter(s), False)

def one_letter_between(s):
    x = list(consume(s, 3))
    for c1, c2, c3 in x:
        if c1 == c3:
            return True
    return False

def isnice2(s):
    t1 = at_least_two_pair(s)
    t2 = one_letter_between(s)
    return t1 and t2

def get_nice_strings(text, pred=isnice1):
    return [ line for line in text.splitlines() if pred(line) ]

def tests():
    assert isnice1('ugknbfddgicrmopn')
    assert isnice1('aaa')
    assert not isnice1('jchzalrnumimnmhp')
    assert not isnice1('haegwjzuvuyypxyu')
    assert not isnice1('dvszwmarrgswjxmb')

    assert at_least_two_pair('xyxy')
    assert at_least_two_pair('aabcdefgaa')
    assert not at_least_two_pair('aaa')

    assert one_letter_between('xyx')
    assert one_letter_between('abcdefeghi')
    assert one_letter_between('aaa')

    assert isnice2('qjhvhtzxzqqjkmpb')
    assert isnice2('xxyxx')
    assert not isnice2('uurcxstgmygtbstg')
    assert not isnice2('ieodomkazucvgmuy')

def part1():
    input = open(os.path.join('inputs', 'day05.input')).read()
    nice_strings = get_nice_strings(input, isnice1)
    print 'Part 1: %s nice strings' % (len(nice_strings), )

def part2():
    input = open(os.path.join('inputs', 'day05.input')).read()
    nice_strings = get_nice_strings(input, isnice2)
    print 'Part 2: %s nice strings' % (len(nice_strings), )

def main():
    tests()
    part1()
    part2()

if __name__ == '__main__':
    main()
