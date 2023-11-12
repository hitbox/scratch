from itertools import chain
from itertools import product
from operator import attrgetter

from .constants import CORNERS
from .constants import LINES
from .constants import MIDPOINTS
from .constants import POINTS
from .constants import SIDES
from .external import pygame

corners = attrgetter(*CORNERS)
lines_getters = [attrgetter(*line) for line in LINES]
midpoints = attrgetter(*MIDPOINTS)
points = attrgetter(*POINTS)
sides = attrgetter(*SIDES)

def hlines(rect):
    """
    Generate the horizontal lines of a rect.
    """
    yield lines_getters[0](rect) # topline
    yield lines_getters[2](rect) # bottomline

def vlines(rect):
    """
    Generate the vertical lines of a rect.
    """
    yield lines_getters[1](rect) # rightline
    yield lines_getters[3](rect) # leftline

def lines(rect):
    """
    Clockwise generator of rect's line segments starting at top.
    """
    for line_getter in lines_getters:
        yield line_getter(rect)

def adjacent_sides(sidename):
    """
    Return the two adjacent sides, attribute names.
    """
    i = SIDES.index(sidename)
    j = (i - 1) % len(SIDES)
    k = (i + 1) % len(SIDES)
    return (SIDES[j], SIDES[k])

def from_points(points):
    """
    Return a new rect from given x,y points. This is like `wrap` except it
    works on points instead of rects.

    :param points: iterable of (x,y) pairs
    """
    xs, ys = zip(*points)
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    width = right - left
    height = bottom - top
    return pygame.Rect(left, top, width, height)

def is_intersect(vert, horz):
    """
    Does vertical and horizontal line segments intersect?
    """
    vertp1, vertp2 = vert
    horzpoint1, horzpoint2 = horz

    vertx = vertp1[0]
    horzleft = horzpoint1[0]
    horzright = horzpoint2[0]

    horzy = horzpoint1[1]
    verttop = vertp1[1]
    vertbottom = vertp2[1]

    return (
        horzleft <= vertx <= horzright
        and
        verttop <= horzy <= vertbottom
    )

def line_intersect(vert, horz):
    """
    Intersection point of vertical and horizontal line segments.
    """
    vertpoint1, vertpoint2 = vert
    horzpoint1, horzpoint2 = horz
    x = vertpoint1[0]
    y = horzpoint1[1]
    return (x, y)

def intersection_points(r1, r2):
    """
    Iterator of points of intersection of rects.
    """
    verts1 = vlines(r1)
    verts2 = vlines(r2)

    horzs1 = hlines(r1)
    horzs2 = hlines(r2)

    return chain(
        (line_intersect(v,h) for v, h in product(verts1, horzs2) if is_intersect(v, h)),
        (line_intersect(v,h) for v, h in product(verts2, horzs1) if is_intersect(v, h)),
    )

def intersection(r1, r2):
    """
    Return new rect of the intersection of two rects.
    """
    if r1 == r2:
        return r1.copy()

    if not r1.colliderect(r2):
        return

    # points where r1 and r2 rects lines intersect
    intersects = intersection_points(r1, r2)
    # points (corners) of r1 that are inside r2
    inside1 = (p1 for p1 in corners(r1) if r2.collidepoint(p1))
    # points of r2 inside r1
    inside2 = (p2 for p2 in corners(r2) if r1.collidepoint(p2))
    # chain them all together...
    points = chain(intersects, inside1, inside2)
    # ...build and return a rect
    rect = from_points(points)
    return rect

def namedpoints(rect):
    """
    `points` with the attribute's name included.
    """
    yield from zip(POINTS, points(rect))

def normalized(start, stop, rect=None):
    """
    Return a pygame.Rect ensuring positive width and height. Modify `rect`
    in-place, if given.
    """
    if rect is None:
        rect = pygame.Rect(0,0,0,0)

    sx, sy = start
    ex, ey = stop

    sx, ex = sorted([sx, ex])
    sy, ey = sorted([sy, ey])

    w = ex - sx
    h = ey - sy
    rect.x = sx
    rect.y = sy
    rect.width = w
    rect.height = h
    return rect

def new(**attrs):
    """
    Convenience func for creating and positioning pygame.Rect all at once.
    """
    # minimum required by pygame
    x = attrs.setdefault('x', 0)
    y = attrs.setdefault('y', 0)
    width = attrs.setdefault('width', 0)
    height = attrs.setdefault('height', 0)

    rect = pygame.Rect(x, y, width, height)

    exclude = ('x', 'y', 'width', 'height')
    keyorder = ['size', 'width', 'height', 'left', 'top']
    keyorder += POINTS
    keyorder += ['center']

    def keyindex(item):
        key, val = item
        return keyorder.index(key)

    items = sorted(
        ((key, val) for key, val in attrs.items() if key not in exclude),
        key = keyindex,
    )
    for key, val in items:
        setattr(rect, key, val)
    return rect

def opposite_point(point):
    """
    Return name of point opposite given.
    """
    i = POINTS.index(point)
    j = (i + len(POINTS) // 2) % len(POINTS)
    opposite = POINTS[j]
    return opposite

def opposite_side(sidename):
    """
    Return the opposite of rect side attribute name.
    """
    i = SIDES.index(sidename)
    j = (i + 2) % len(SIDES)
    return SIDES[j]

def opposite_midpoint(midname):
    """
    """
    i = MIDPOINTS.index(midname)
    j = (i + len(MIDPOINTS) + 2) % len(MIDPOINTS)
    return MIDPOINTS[j]

def wrap_python(rects):
    """
    Wrap iterable of rects with one large rect.
    """
    sides_of_rects = map(sides, rects)
    tops, rights, bottoms, lefts = zip(*sides_of_rects)
    top = min(tops)
    right = max(rights)
    bottom = max(bottoms)
    left = min(lefts)
    width = right - left
    height = bottom - top
    return pygame.Rect(left, top, width, height)

def wrap_pygame(rects):
    """
    Convenience for `pygame.Rect.unionall`. `unionall` requires the instance
    Rect. This picks off the first rect and uses it to unionall the remaining.
    """
    # see timeit/wrap.sh for huge speed up
    rect, *rects = rects
    return rect.unionall(rects)

wrap = wrap_pygame
