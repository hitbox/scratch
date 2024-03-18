import math

from itertools import product
from itertools import repeat

NAMED = {
    ( 0, -1): 'above',
    ( 1, -1): 'right-above',
    ( 1,  0): 'right',
    ( 1,  1): 'right-below',
    ( 0,  1): 'below',
    (-1,  1): 'left-below',
    (-1,  0): 'left',
    (-1, -1): 'left-above',
}

def clockwise(point):
    x, y = point
    return math.atan2(y, x)

values = range(-1, 2)

def rotlist(list_, offset=1):
    "rotate list"
    return list_[offset:] + list_[:offset]

# two imports, slightly shorter function
def all_directions_it():
    for d in product(*repeat(values, 2)):
        if d != (0, 0):
            yield d

# no imports, nested loops, walrus operator
def all_directions():
    for y in values:
        for x in values:
            if (x, y) != (0, 0):
                yield (x, y)

assert rotlist(sorted(all_directions(), key=clockwise)) == list(NAMED.keys())

def by_angle(with_diagonal=False, clockwise=False, start=0):
    sign = -1 if clockwise else 1

    if with_diagonal:
        step = 45 * sign
    else:
        step = 90 * sign

    stop = sign * 360 + start
    angles = range(start, stop, step)

    def normalize(value):
        return int(math.copysign(abs(value) > .5, value))

    for angle in angles:
        r = math.radians(angle)
        x = normalize(math.cos(r))
        y = normalize(math.sin(r))
        yield (x, y)

def shorthand_order(with_diagonal=False):
    # clockwise from top/up, like css shorthand
    return by_angle(with_diagonal, clockwise=True, start=90)

assert list(by_angle()) == [(1,0), (0, 1), (-1, 0), (0, -1)]

a = list(by_angle(with_diagonal=True))
b = [(1,0), (1,1), (0, 1), (-1,1), (-1, 0), (-1,-1), (0, -1), (1,-1)]
assert a == b, a


print(list(shorthand_order(with_diagonal=True)))
