"""
--- Day 3: Squares With Three Sides ---

Now that you can think clearly, you move deeper into the labyrinth of hallways
and office furniture that makes up this part of Easter Bunny HQ. This must be a
graphic design department; the walls are covered in specifications for
sides.

Or are they?

The design document gives the side lengths of each triangle it describes,
but... 5 10 25? Some of these aren't sides. You can't help but mark the
impossible ones.

In a valid triangle, the sum of any two sides must be larger than the remaining
side. For example, the "triangle" given above is impossible, because 5 + 10 is
not larger than 25.

In your puzzle input, how many of the listed sides are possible?

--- Part Two ---

Now that you've helpfully marked up their design documents, it occurs to you
that triangles are specified in groups of three vertically. Each set of three
numbers in a column specifies a triangle. Rows are unrelated.

For example, given the following specification, numbers with the same hundreds
digit would be part of the same triangle:

101 301 501
102 302 502
103 303 503
201 401 601
202 402 602
203 403 603

In your puzzle input, and instead reading by columns, how many of the listed
triangles are possible?
"""
import os
import argparse
import logging
from itertools import tee

def istriangle(s1, s2, s3):
    if (s1 + s2) <= s3:
        return False
    if (s1 + s3) <= s2:
        return False
    if (s2 + s3) <= s1:
        return False
    return True

def tests():
    assert not istriangle(5, 10, 25)

    weird = "101 301 501\n102 302 502\n103 303 503\n201 401 601\n202 402 602\n203 403 603"
    expected = [(101, 102, 103),
                (201, 202, 203),
                (301, 302, 303),
                (401, 402, 403),
                (501, 502, 503),
                (601, 602, 603)]
    sides = list(sides_by_column(weird))
    log = logging.getLogger('tests')
    log.debug(sides)
    assert sides == expected

def sides_by_row(text):
    return (tuple(map(int, line.split())) for line in text.splitlines())

def threewise(iterable):
    # NOTE: This started off built by the example of pairwise.
    #       https://docs.python.org/3/library/itertools.html
    #       Had to realize that it needs to be iterated by twos too.
    a, b, c = tee(iterable, 3)
    next(b, None)
    next(c, None)
    next(c, None)
    tups = zip(a, b, c)
    for tup in tups:
        yield tup
        next(tups, None)
        next(tups, None)

def sides_by_column(text):
    log = logging.getLogger('sides_by_column')

    for column in zip(*sides_by_row(text)):
        log.debug('column: %s' % (column, ))
        sides = threewise(column)
        for side in sides:
            log.debug('side: %s' % (side, ))
            yield side

def load():
    return open(os.path.join(os.path.dirname(__file__), 'input.txt')).read()

def count(iterable):
    return sum(1 for _ in iterable)

def part1():
    n = count( s for s in sides_by_row(load()) if istriangle(*s) )
    print('Day 3, part 1: %s valid sides.' % n)

def part2():
    sides = sides_by_column(load())
    n = count( s for s in sides if istriangle(*s) )
    print('Day 3, part 2: %s valid sides (columnar).' % n)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Show debug logging.')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    tests()
    part1()
    part2()
