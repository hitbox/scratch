#!/usr/bin/env python2
import os
from pprint import pprint as pp
from adventlib import input_path

range = xrange

CODE = {'#': True, '.': False}
DISPLAY = {v:k for k,v in CODE.items()}

EXAMPLE = """\
.#.#.#
...##.
#....#
..#...
#.#..#
####.."""

def size(s):
    return len(s.splitlines()[0])

def parse(s):
    for y, line in enumerate(s.splitlines()):
        for x, char in enumerate(line):
            yield ( (x, y), CODE[char] )

NEIGHBOR_DELTAS = [(x, y) for x in range(-1, 2) for y in range(-1, 2) if not x == y == 0]

def neighbors(data, x, y):
    return (data[(x+dx,y+dy)] for dx,dy in NEIGHBOR_DELTAS if (x+dx,y+dy) in data)

def coordinates(data, n):
    n = list(range(n))
    for x in n:
        for y in n:
            yield (x, y)

def nextstate(data, n, stuck=False):
    newstate = {}
    upper = n - 1
    for x, y in coordinates(data, n):
        if stuck and (x, y) in ( (0, 0), (0, upper), (upper, 0), (upper, upper) ):
            newstate[(x, y)] = True
            continue

        light = data[(x,y)]

        neighbors_on = sum(n for n in neighbors(data, x, y) if n)
        if light:
            light = neighbors_on in (2, 3)
        else:
            light = neighbors_on == 3
        newstate[(x,y)] = light

    return newstate

def display(data, n):
    n = list(range(n))
    return '\n'.join(''.join([DISPLAY[data[(x,y)]] for x in n]) for y in n)

def runtest(data, n, stuck=False):
    for _ in range(5):
        data = nextstate(data, n, stuck)
    return data

def test():
    n = size(EXAMPLE)
    data = runtest(dict(parse(EXAMPLE)), n)
    assert display(data, n) == """\
......
......
..##..
..##..
......
......"""

    data = dict(parse(EXAMPLE))
    data[(0, 0)] = True
    data[(0, 5)] = True
    data[(5, 0)] = True
    data[(5, 5)] = True
    data = runtest(data, n, True)
    assert display(data, n) == """\
##.###
.##..#
.##...
.##...
#.#...
##...#"""

def original_data():
    with open(input_path(__file__, 1)) as f:
        return dict(parse(f.read()))

def main():
    data = original_data()
    n = 100
    for _ in range(100):
        data = nextstate(data, n)

    lights_on = sum(1 if v else 0 for v in data.values())
    print 'Part 1: %s lights on' % (lights_on, )


    data = original_data()
    data[(0, 0)] = True
    data[(0, n)] = True
    data[(n, 0)] = True
    data[(n, n)] = True
    for _ in range(100):
        data = nextstate(data, n, True)
    lights_on = sum(1 if v else 0 for v in data.values())
    print 'Part 2: %s lights on' % (lights_on, )

if __name__ == '__main__':
    test()
    main()
