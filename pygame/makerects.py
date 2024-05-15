import argparse
import itertools as it
import math
import operator as op

import pygamelib

def copy(rect, string):
    x, y, w, h = rect
    if string.startswith('d'):
        return (x, y + h, w, h)
    elif string.startswith('l'):
        return (x - w, y, w, h)
    elif string.startswith('r'):
        return (x + w, y, w, h)
    elif string.startswith('u'):
        return (x, y - h, w, h)

def elementwise(operation, *args):
    return tuple(map(operation, *args))

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'size',
        type = pygamelib.sizetype(),
    )
    parser.add_argument(
        'moves',
        choices = list('dlru') + ['down', 'left', 'right', 'up'],
        nargs = '*',
    )
    args = parser.parse_args(argv)

    moves = [name[0] for name in args.moves]

    points = [(0,0)]
    for move in moves:
        if move == 'd':
            dx = 0
            dy = 1
        elif move == 'l':
            dx = -1
            dy = 0
        elif move == 'r':
            dx = 1
            dy = 0
        elif move == 'u':
            dx = 0
            dy = -1
        points.append(elementwise(op.add, points[-1], (dx, dy)))

    for p1, p2, p3 in pygamelib.nwise(points, 3):
        if all((p1, p2, p3)):
            angle = pygamelib.corner_angle(p1, p2, p3)
            print((p1, p2, p3, math.degrees(angle)))

if __name__ == '__main__':
    main()
