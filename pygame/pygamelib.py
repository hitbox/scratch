import contextlib
import itertools as it
import operator as op
import os

# silence and import pygame
with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

# clean up namespace
del contextlib
del os

def is_point_name(name):
    """
    Name contains a side name but is not exactly the side name.
    """
    return any(side in name for side in SIDES if name != side)

def point_attrs(sides):
    """
    Generate the attribute names of the points on a rect.
    """
    for i, side in enumerate(sides):
        if side in ('top', 'bottom'):
            yield side + sides[(i - 1) % 4]
            yield 'mid' + side
            yield side + sides[(i + 1) % 4]
        else:
            yield 'mid' + side

def opposites(indexable):
    """
    Generate two-tuples of items and their opposite from an indexable. Opposite
    being halfway around the indexable.
    """
    n = len(indexable)
    assert n % 2 == 0
    half_n = n // 2
    for i, item1 in enumerate(indexable):
        j = (i + half_n) % n
        item2 = indexable[j]
        yield (item1, item2)

def make_rect(rect=None, **kwargs):
    if rect is None:
        rect = empty_rect
    rect = rect.copy()
    for key, val in kwargs.items():
        setattr(rect, key, val)
    return rect

def from_points(x1, y1, x2, y2):
    w = x2 - x1
    h = y2 - y1
    return (x1, y1, w, h)

def aggsides(func, *rects):
    """
    execute `func` on all sides of all rects returning unpackable of
    `func(tops), func(rights), func(bottoms), func(lefts)`
    """
    return map(func, *map(sides, rects))

def minsides(*rects):
    """
    minimum of all four rects' sides
    """
    return aggsides(min, *rects)

def maxsides(*rects):
    """
    maximum of all four rects' sides
    """
    return aggsides(max, *rects)

def iter_rect_diffs(rect, inside):
    """
    Generate eight rects resulting from "subtracting" `rect` from `inside`.
    """
    _, minright, minbottom, _ = minsides(rect, inside)
    maxtop, _, _, maxleft = maxsides(rect, inside)
    # topleft
    yield from_points(*inside.topleft, *rect.topleft)
    # top
    yield from_points(maxleft, inside.top, minright, rect.top)
    # topright
    yield from_points(minright, inside.top, inside.right, rect.top)
    # right
    yield from_points(minright, maxtop, inside.right, minbottom)
    # bottomright
    yield from_points(*rect.bottomright, *inside.bottomright)
    # bottom
    yield from_points(maxleft, rect.bottom, minright, inside.bottom)
    # bottomleft
    yield from_points(inside.left, rect.bottom, rect.left, inside.bottom)
    # left
    yield from_points(inside.left, maxtop, rect.left, minbottom)

def surrounding(rect):
    # going around the original rect's points...
    for attr, oppo in POINTS.items():
        kwargs = {oppo: getattr(rect, attr)}
        # ...create new rect of the same size, aligned to the opposite point
        yield make_rect(size=rect.size, **kwargs)

def area(rect):
    return rect.width * rect.height

def overlaps(rects):
    for r1, r2 in it.combinations(rects, 2):
        clipping = r1.clip(r2)
        if clipping:
            yield (r1, r2, clipping)

# clockwise ordered rect side attribute names mapped with their opposites
SIDES = dict(opposites(['top', 'right', 'bottom', 'left']))

# clockwise ordered rect point attribute names mapped with their opposites
POINTS = dict(opposites(tuple(point_attrs(tuple(SIDES)))))

empty_rect = pygame.Rect((0,)*4)

points = op.attrgetter(*POINTS)

sides = op.attrgetter(*SIDES)

class MethodName:
    """
    Callable to create a method name from a pygame event.
    """

    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, event):
        event_name = pygame.event.event_name(event.type)
        method_name = self.prefix + event_name.lower()
        return method_name


def dispatch(obj, event):
    method_name = default_methodname(event)
    method = getattr(obj, method_name, None)
    if method is not None:
        method(event)

default_methodname = MethodName(prefix='do_')

class Engine:

    def __init__(self):
        self.running = False

    def run(self, state):
        state.start(engine=self)
        self.running = True
        while self.running:
            state.update()

    def stop(self):
        self.running = False


class ColorSpace:
    """
    Convenience to get one of the space representations of a pygame color,
    minus the alpha if present.
    """

    spaces = ['cmy', 'hsl', 'hsv', 'rgb']
    remove_alpha = ['hsl', 'hsv', 'rgb']

    def __init__(self, space):
        assert space in self.spaces

        attr = space
        if space in ('hsl', 'hsv'):
            attr += 'a'
        self.get_attr = op.attrgetter(attr)

    def __call__(self, color):
        color = pygame.Color(color)
        return self.get_attr(color)[:3]


# pygame.Color is not hashable

COLORSTHE = {
    tuple(pygame.Color(color)): name
    for name, color in pygame.color.THECOLORS.items()
}

def color_name(color):
    color = pygame.Color(color)
    return COLORSTHE[tuple(color)]

interesting_colors_pattern = r'gr[ae]y|white|black|silver|light|medium|dark|\d|red|green|blue'

def interesting_color(color):
    """
    Ignoring alpha, rgb values are not all the same.
    """
    color = pygame.Color(color)
    return len(set(color[:3])) != 1
