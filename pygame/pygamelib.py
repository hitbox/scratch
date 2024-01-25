import argparse
import contextlib
import itertools as it
import math
import operator as op
import os
import random
import string
import sys
import unittest
import xml.etree.ElementTree as ET

from collections import namedtuple

# silently import pygame
with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

# clean up namespace
del contextlib
del os

class TestGroupbyColumns(unittest.TestCase):

    def test_vs_sloppy(self):
        # testing newer groupby columns function against older working one
        items = 'abcdabcdabcd'
        ncols = 5
        result1 = groupby_columns(items, ncols)
        result2 = groupby_columns_reference(items, ncols)
        self.assertEqual(result1, result2)


class TestMergeRanges(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(merge_ranges([]), set())

    def test_sequence(self):
        expect = [(0,3)]
        test = list(merge_ranges([(0,1),(1,2),(2,3)]))
        self.assertEqual(test, expect)

    def test_identity(self):
        ranges = set([(0,1),(2,3),(4,5)])
        test = merge_ranges(ranges)
        self.assertEqual(test, ranges)

    def test_overlapping(self):
        test = merge_ranges([(0,3),(2,5),(3,10)])
        self.assertEqual(test, set([(0,10)]))
        test = merge_ranges([(0,10),(1,2),(3,5),(4,8)])
        self.assertEqual(test, set([(0,10)]))


class TestMergeRects(unittest.TestCase):

    def test_merge_rects_none(self):
        self.assertIsNone(
            merge_rects((0, 0, 10, 10), (15, 15, 10, 10))
        )

    def test_merge_rects_leftright(self):
        self.assertEqual(
            merge_rects((0, 0, 10, 10), (10, 0, 10, 10)),
            (0, 0, 20, 10),
        )
        self.assertEqual(
            merge_rects((10, 0, 10, 10), (0, 0, 10, 10)),
            (0, 0, 20, 10),
        )

    def test_merge_rects_topbottom(self):
        self.assertEqual(
            merge_rects((0, 0, 10, 10), (0, 10, 10, 10)),
            (0, 0, 10, 20),
        )

    def test_merge_rects_diagonal_is_none(self):
        # diagonals do not merge
        self.assertIsNone(
            merge_rects((0, 0, 10, 10), (10, 10, 10, 10)),
        )


class TestMergeAllRects(unittest.TestCase):

    def test_merge_all_none(self):
        no_merges_rects = [
            (0, 0, 10, 10),
            (20, 0, 10, 10),
            (0, 20, 10, 10),
        ]
        self.assertEqual(
            merge_all_rects(no_merges_rects),
            no_merges_rects,
        )

    def test_merge_all_square(self):
        square = [
            (0, 0, 10, 10),
            (10, 0, 10, 10),
            (0, 10, 10, 10),
            (10, 10, 10, 10),
        ]
        self.assertEqual(
            merge_all_rects(square),
            [(0, 0, 20, 20)],
        )

    def test_merge_all_four_to_two(self):
        rects = [
            (0, 0, 10, 10),
            (10, 0, 10, 10),
            (20, 20, 10, 10),
        ]
        # set to disregard order
        self.assertEqual(
            set(merge_all_rects(rects)),
            set([
                (0, 0, 20, 10),
                (20, 20, 10, 10),
            ]),
        )


def intargs(string):
    return map(int, string.replace(',', ' ').split())

class sizetype:

    def __init__(self, n=2):
        self.n = n

    def __call__(self, string):
        size = tuple(intargs(string))
        while len(size) < self.n:
            size += size
        return size


def chunk(iterable, n):
    iterable = iter(iterable)
    stop = False
    while not stop:
        chunk = []
        for _ in range(n):
            try:
                chunk.append(next(iterable))
            except StopIteration:
                stop = True
        if chunk:
            yield tuple(chunk)

def rfinditer(s, subs, *args):
    # many version of str.rfind
    for sub in subs:
        index = s.rfind(sub, *args)
        yield index

def finditer(s, subs, *args):
    # many version of str.find
    for sub in subs:
        index = s.find(sub, *args)
        yield index

def rect_type(string):
    """
    pygame Rect arguments as from command line or text file.
    """
    return pygame.Rect(*intargs(string))

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

def mix(x, a, b):
    """
    Return the percent of x between a and b.
    """
    return a * (1 - x) + b * x

def remap(x, a, b, c, d):
    """
    Return x from range a and b to range c and d.
    """
    return x*(d-c)/(b-a) + c-a*(d-c)/(b-a)

def opposites(indexable):
    """
    Generate two-tuples of items and their opposite from an indexable. Opposite
    being halfway around the indexable.
    """
    # XXX: `opposite_item` func below
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

def wrap(rects):
    tops, rights, bottoms, lefts = zip(*map(sides, rects))
    x = min(lefts)
    y = min(tops)
    right = max(rights)
    bottom = max(bottoms)
    width = right - x
    height = bottom - y
    return (x, y, width, height)

def iter_rect_diffs(inside, outside):
    """
    Generate eight rects resulting from "subtracting" `inside` from `outside`.
    """
    inside, outside = map(pygame.Rect, [inside, outside])
    _, minright, minbottom, _ = minsides(inside, outside)
    maxtop, _, _, maxleft = maxsides(inside, outside)
    # topleft
    yield from_points(*outside.topleft, *inside.topleft)
    # top
    yield from_points(maxleft, outside.top, minright, inside.top)
    # topright
    yield from_points(minright, outside.top, outside.right, inside.top)
    # right
    yield from_points(minright, maxtop, outside.right, minbottom)
    # bottomright
    yield from_points(*inside.bottomright, *outside.bottomright)
    # bottom
    yield from_points(maxleft, inside.bottom, minright, outside.bottom)
    # bottomleft
    yield from_points(outside.left, inside.bottom, inside.left, outside.bottom)
    # left
    yield from_points(outside.left, maxtop, inside.left, minbottom)

def area(rect):
    _, _, w, h = rect
    return w * h

def overlaps(rects):
    for r1, r2 in it.combinations(rects, 2):
        clipping = r1.clip(r2)
        if clipping:
            yield (r1, r2, clipping)

# clockwise ordered rect side attribute names mapped with their opposites
SIDENAMES = ['top', 'right', 'bottom', 'left']
SIDES = dict(opposites(SIDENAMES))

def opposite_item(list_, item):
    """
    Return the item halfway around the indexable from the given item.
    """
    # XXX: `opposites` func above
    n = len(list_)
    assert n % 2 == 0
    index = list_.index(item)
    return list_[(index + n // 2) % n]

# opposite sides by index
SIDENAMES_OPPO = [opposite_item(SIDENAMES, item) for item in SIDENAMES]

# clockwise ordered rect point attribute names mapped with their opposites
POINTS = dict(opposites(tuple(point_attrs(tuple(SIDES)))))

empty_rect = pygame.Rect((0,)*4)

points = op.attrgetter(*POINTS)

sides = op.attrgetter(*SIDES)

def side_lines(rect):
    rect = pygame.Rect(rect)
    yield (rect.topleft, rect.topright)
    yield (rect.topright, rect.bottomright)
    yield (rect.bottomright, rect.bottomleft)
    yield (rect.bottomleft, rect.topleft)

def line_rect_intersections(line, rect):
    (x3, y3), (x4, y4) = line
    for rectline in side_lines(rect):
        (x1, y1), (x2, y2) = rectline
        intersection = line_line_intersection(x1, y1, x2, y2, x3, y3, x4, y4)
        if intersection:
            yield intersection

CORNERNAMES = ['topleft', 'topright', 'bottomright', 'bottomleft']

def steppairs(start, stop, step):
    # range(0, 360, 30) -> (0, 30), (30, 60), ..., (330, 360)
    for i in range(start, stop, step):
        yield (i, i+step)

QUADRANT_DEGREES = dict(zip(
    ['topright', 'topleft', 'bottomleft', 'bottomright'],
    steppairs(0, 360, 90),
))

# line pairs as rect attribute names to draw each quadrant of a rect

CORNERLINES = dict(
    topleft = (('midleft', 'topleft'), ('topleft', 'midtop')),
    topright = (('midtop', 'topright'), ('topright', 'midright')),
    bottomright = (('midright', 'bottomright'), ('bottomright', 'midbottom')),
    bottomleft = (('midbottom', 'bottomleft'), ('bottomleft', 'midleft')),
)

def rects(images, **kwargs):
    return map(op.methodcaller('get_rect'), images, **kwargs)

def sides(rect):
    # overwrite to remain compatible with four-tuple rects
    left, top, w, h = rect
    right = left + w
    bottom = top + h
    return (top, right, bottom, left)

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


default_methodname = MethodName(prefix='do_')

def dispatch(obj, event):
    method_name = default_methodname(event)
    method = getattr(obj, method_name, None)
    if method is not None:
        method(event)

def _post(event_type):
    pygame.event.post(pygame.event.Event(event_type))

def post_quit():
    _post(pygame.QUIT)

def post_videoexpose():
    _post(pygame.VIDEOEXPOSE)

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


class DemoBase:

    def start(self, engine):
        self.engine = engine
        self.screen = pygame.display.get_surface()
        self.window = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.framerate = 60
        self.elapsed = None

    def update(self):
        self.elapsed = self.clock.tick(self.framerate)
        for event in pygame.event.get():
            dispatch(self, event)


class TestInputLine(unittest.TestCase):

    def setUp(self):
        self.input_line = InputLine()

    def test_addchar(self):
        self.input_line.addchar('a')
        self.assertEqual(self.input_line.line, 'a')

    def test_insert_after_left(self):
        self.input_line.addchar('b')
        self.input_line.caretleft()
        self.input_line.addchar('a')
        self.assertEqual(self.input_line.line, 'ab')

    def test_insert_after_right(self):
        self.input_line.addchar('a')
        self.input_line.addchar('c')
        self.input_line.caretleft()
        self.input_line.caretleft()
        self.input_line.caretright()
        self.input_line.addchar('b')
        self.assertEqual(self.input_line.line, 'abc')

    def test_backspace(self):
        self.input_line.addchar('a')
        self.input_line.addchar('b')
        self.input_line.backspace()
        self.assertEqual(self.input_line.line, 'a')


class InputLine:

    def __init__(self):
        self.line = ''
        self.caret = None
        self.jumpchars = string.punctuation + string.whitespace

    def split(self):
        if self.caret is None:
            return (self.line, '')
        else:
            return (self.line[:self.caret], self.line[self.caret:])

    def addchar(self, char):
        before, after = self.split()
        self.line = before + char + after
        if self.caret is not None:
            self.caret += 1

    def backspace(self):
        before, after = self.split()
        self.line = before[:-1] + after
        if self.caret is not None:
            self.caret -= 1

    def delete(self):
        before, after = self.split()
        self.line = before + after[1:]

    def caretleft(self):
        if self.caret is None:
            self.caret = len(self.line) - 1
        if self.caret > 0:
            self.caret -= 1

    def caretright(self):
        if self.caret is not None:
            self.caret += 1

    def jumpleft(self):
        indexes = rfinditer(self.line, self.jumpchars, 0, self.caret)
        indexes = [index for index in indexes if index > -1]
        self.caret = max(indexes, default=0)

    def jumpright(self):
        if self.caret is not None:
            indexes = finditer(self.line, self.jumpchars, self.caret+1, None)
            indexes = [index for index in indexes if index > -1]
            self.caret = min(indexes, default=None)


class Readline:

    def __init__(self, linecallback=None):
        self.linecallback = linecallback
        self.more = False
        self.input_index = 0
        self.input_lines = [InputLine()]

    def prompt(self):
        if self.more:
            return sys.ps2
        else:
            return sys.ps1

    def input_line(self):
        return self.input_lines[self.input_index].line

    def full_input_line(self):
        return self.prompt() + self.input_line()

    def do_keydown(self, event):
        input_line = self.input_lines[self.input_index]
        if event.key == pygame.K_RETURN:
            if input_line.line or self.more:
                if callable(self.linecallback):
                    self.linecallback(input_line.line)
                self.input_index += 1
                self.input_lines.append(InputLine())
        elif event.key == pygame.K_BACKSPACE:
            input_line.backspace()
        elif event.key == pygame.K_DELETE:
            input_line.delete()
        elif event.key == pygame.K_UP:
            if self.input_index > 0:
                self.input_index -= 1
        elif event.key == pygame.K_DOWN:
            if self.input_index < len(self.input_lines) - 1:
                self.input_index += 1
        elif event.key == pygame.K_LEFT:
            if event.mod & pygame.KMOD_CTRL:
                input_line.jumpleft()
            else:
                input_line.caretleft()
        elif event.key == pygame.K_RIGHT:
            if event.mod & pygame.KMOD_CTRL:
                input_line.jumpright()
            else:
                input_line.caretright()
        else:
            input_line.addchar(event.unicode)


class BrowseBase:
    """
    Convenience state to display blitables, drag to move, and quit cleanly.
    """

    def start(self, engine):
        self.engine = engine
        self.screen = pygame.display.get_surface()
        self.window = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.framerate = 60
        if not hasattr(self, 'offset'):
            self.offset = pygame.Vector2()

    def update(self):
        self.clock.tick(self.framerate)
        for event in pygame.event.get():
            dispatch(self, event)

    @property
    def blits(self):
        # TODO
        # - make subclasses implement drawing
        return ((image, rect.topleft - self.offset) for image, rect in self._blits)

    def do_videoexpose(self, event):
        self.screen.fill('black')
        self.screen.blits(self.blits)
        pygame.display.flip()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            post_quit()

    def do_mousemotion(self, event):
        if event.buttons[0]:
            self.offset -= event.rel
            post_videoexpose()


class RectRenderer:
    """
    Simple rect renderer with highlighting.
    """

    def __init__(self, offset=(0,0), highlight=None, highlight_color='magenta'):
        self.offset = pygame.Vector2(offset)
        self.highlight = highlight
        self.highlight_color = highlight_color

    def __call__(self, surface, color, fill, rects):
        ox, oy = self.offset
        drawn_rects = []
        for rect in rects:
            if rect is self.highlight:
                _color = self.highlight_color
                _fill = 0
            else:
                _color = color
                _fill = fill
            (x, y, w, h) = rect
            rect = (x+ox, y+oy, w, h)
            drawn = pygame.draw.rect(surface, _color, rect, _fill)
            drawn_rects.append(drawn)
        return drawn_rects


class ColorSpace:
    """
    Convenience to get one of the space representations of a pygame color,
    minus the alpha if present.
    """

    spaces = ['cmy', 'hsl', 'hsv', 'rgb']
    remove_alpha = ['hsl', 'hsv', 'rgb']

    def __init__(self, space):
        assert space in self.spaces
        self.space = space
        if self.space == 'rgb':
            # for whatever reason these are all separate in pygame.Color
            self.get_attr = op.attrgetter(*self.space)
        else:
            attr = self.space
            if self.space in ('hsl', 'hsv'):
                attr += 'a'
            self.get_attr = op.attrgetter(attr)

    def __call__(self, color):
        color = pygame.Color(color)
        return self.get_attr(color)[:3]

def colortext(color_key):
    if color_key.space in ('cmy', 'hsl', 'hsv'):
        def _colortext(color):
            return ' '.join(f'{val:.0f}' for val in color_key(color))
    else:
        def _colortext(color):
            return ' '.join(map(str, color_key(color)))
    return _colortext

def hue(color):
    color = pygame.Color(color)
    hue, *_ = color.hsva
    return hue

def saturation(color):
    color = pygame.Color(color)
    _, saturation, *_ = color.hsva
    return saturation

def value(color):
    color = pygame.Color(color)
    _, _, value, _ = color.hsva
    return value

# pygame.Color is not hashable

COLORSTHE = {
    tuple(pygame.Color(color)): name
    for name, color in pygame.color.THECOLORS.items()
}

def color_name(color):
    color = pygame.Color(color)
    return COLORSTHE[tuple(color)]

interesting_colors_pattern = '|'.join([
    r'\d',
    'black',
    'blue',
    'dark',
    'gr[ae]y',
    'green',
    'light',
    'medium',
    'red',
    'silver',
    'white',
])

def interesting_color(color):
    """
    rgb values are not all the same meaning *NOT* some shade of white.
    """
    color = pygame.Color(color)
    return len(set(color[:3])) != 1

def flow_leftright(rects, gap=0):
    for r1, r2 in it.pairwise(rects):
        r2.left = r1.right + gap

def flow_topbottom(rects, gap=0):
    for r1, r2 in it.pairwise(rects):
        r2.top = r1.bottom + gap

def enumerate_grid(iterable, ncols):
    for index, item in enumerate(iterable):
        rowcol = divmod(index, ncols)
        yield (rowcol, item)

def select_row(items, ncols, row):
    for (j, i), item in enumerate_grid(items, ncols):
        if j == row:
            yield item

def select_col(items, ncols, col):
    for (j, i), item in enumerate_grid(items, ncols):
        if i == col:
            yield item

def sorted_groupby(iterable, key=None, reverse=False):
    """
    Convenience for sorting and then grouping.
    """
    return it.groupby(sorted(iterable, key=key, reverse=reverse), key=key)

def groupby_columns_reference(items, ncols):
    # the original effort that worked
    nrows = math.ceil(len(items) / ncols)
    rows = [list(select_row(items, ncols, row)) for row in range(nrows)]
    cols = [list(select_col(items, ncols, col)) for col in range(ncols)]
    return (rows, cols)

def groupby_columns(items, ncols):
    # two tuples matched by index to items
    def rowcol(index):
        return divmod(index, ncols)

    rows, cols = zip(*map(rowcol, range(len(items))))

    # NOTE
    # - must consider duplicate items
    # - would like to do something like `list.index(item)` for the key func but
    #   it returns the first match
    # - so keep the item and row or col indexes together and strip them later.
    first = op.itemgetter(0)
    rows = sorted_groupby(zip(rows, items), key=first)
    cols = sorted_groupby(zip(cols, items), key=first)

    # consume groupings, ignorning key, and then stripping the key associated
    # with items off
    rows = [[item for _, item in group] for _, group in rows]
    cols = [[item for _, item in group] for _, group in cols]

    return (rows, cols)

def rowcolwraps(row_rects, col_rects):
    row_wraps = list(map(pygame.Rect, map(wrap, row_rects)))
    col_wraps = list(map(pygame.Rect, map(wrap, col_rects)))
    return (row_wraps, col_wraps)

def arrange_columns(rects, ncols, colattr, rowattr):
    """
    :param rects: update rects arranged in a grid
    :param ncols: number of columns
    :param colattr: attribute to align rects in columns
    :param rowattr: attribute to align rects in rows
    """
    row_rects, col_rects = groupby_columns(rects, ncols)

    row_wraps = list(map(pygame.Rect, map(wrap, row_rects)))
    col_wraps = list(map(pygame.Rect, map(wrap, col_rects)))

    flow_topbottom(row_wraps)
    flow_leftright(col_wraps)

    # align item rects inside their cells
    for row, _rects in zip(row_wraps, row_rects):
        for rect in _rects:
            setattr(rect, rowattr, getattr(row, rowattr))

    for column, _rects in zip(col_wraps, col_rects):
        for rect in _rects:
            setattr(rect, colattr, getattr(column, colattr))

def make_blitables_from_font(lines, font, color, antialias=True):
    images = [font.render(line, antialias, color) for line in lines]
    rects = [image.get_rect() for image in images]
    flow_topbottom(rects)
    return (images, rects)

def move_as_one(rects, **kwargs):
    orig = pygame.Rect(wrap(rects))
    dest = make_rect(orig, **kwargs)
    delta = pygame.Vector2(dest.topleft) - orig.topleft
    for rect in rects:
        rect.topleft += delta

def render_color(
    font,
    fill_color,
    name,
    scale,
    text_color = 'white',
    shade_color = 'black',
    shade_amount = 0.50,
    text_align = 'center',
    antialias = True,
):
    """
    Render an image with the name of the color it is filled with.
    """
    size = pygame.Vector2(font.size(name)).elementwise() * scale
    image = pygame.Surface(tuple(size), pygame.SRCALPHA)
    image.fill(fill_color)
    rect = image.get_rect()
    background = fill_color.lerp(shade_color, shade_amount)
    text = font.render(name, antialias, text_color, background)
    pos = text.get_rect(**{text_align: getattr(rect, text_align)})
    image.blit(text, pos)
    return image

def centered_offset(rects, window):
    """
    Offset vector for a window rect centered on a group of rects.
    """
    rect = pygame.Rect(wrap(rects))
    rect.center = window.center
    return -pygame.Vector2(rect.topleft)

def line_center(line):
    (x1, y1), (x2, y2) = line
    return ((x2 - x1) / 2 + x1, (y2 - y1) / 2 + y1)

def mergeable(range1, range2):
    """
    Are these ranges overlapping?
    """
    start1, stop1 = range1
    start2, stop2 = range2
    return not (start1 > stop2 or stop1 < start2)

def merge_ranges(ranges):
    ranges = set(ranges)
    if not ranges:
        return ranges
    while ranges:
        combos = it.combinations(ranges, 2)
        mergeables = set((r1, r2) for r1, r2 in combos if mergeable(r1, r2))
        if not mergeables:
            return ranges
        for r1, r2 in mergeables:
            if r1 in ranges:
                ranges.remove(r1)
            if r2 in ranges:
                ranges.remove(r2)
            ranges.add((min(*r1, *r2), max(*r1, *r2)))

def mergeable_rects(r1, r2):
    t1, t1, w1, h1 = r1
    t2, t2, w2, h2 = r2
    r1 = t1 + w1
    b1 = t1 + h1
    r2 = t2 + w2
    b2 = t2 + h2
    return (
        # same width sharing top or bottom
        (w1 == w2 and (t1 == b2 or t2 == b1))
        or
        # same height sharing left or right
        (h1 == h2 and (t1 == r2 or t2 == r1))
    )

def merge_rects(rect1, rect2):
    l1, t1, w1, h1 = rect1
    l2, t2, w2, h2 = rect2
    r1 = l1 + w1
    b1 = t1 + h1
    r2 = l2 + w2
    b2 = t2 + h2
    if (w1 == w2 and l1 == l2 and (t1 == b2 or t2 == b1)):
        # same width, same left and sharing top/bottom
        return (l1, min(t1, t2), w1, h1 + h2)
    elif (h1 == h2 and t1 == t2 and (l1 == r2 or l2 == r1)):
        # same height, same top and sharing left/right
        return (min(l1, l2), t1, w1 + w2, h1)

def merge_all_rects(rects):
    merged = list(rects)
    while len(merged) > 1:
        for rect1, rect2 in it.combinations(merged, 2):
            merge_result = merge_rects(rect1, rect2)
            if merge_result:
                if rect1 in merged:
                    merged.remove(rect1)
                if rect2 in merged:
                    merged.remove(rect2)
                merged.append(merge_result)
                break
        else:
            # nothing merged because no break so stop
            break
    return merged

def rectquadrants(rect):
    x, y, w, h = rect
    hw = w / 2
    hh = h / 2
    # topleft
    yield (x, y, hw, hh)
    # topright
    yield (hw, y, hw, hh)
    # bottomright
    yield (hw, hh, hw, hh)
    # bottomleft
    yield (x, hh, hw, hh)

def rectwalls(rect):
    """
    Generate square rects from a rect's sides.
    """
    x, y, w, h = rect
    # top
    yield (x, y - w, w, w)
    # right
    yield (x + w, y, h, h)
    # bottom
    yield (x, y + h, w, w)
    # left
    yield (x - h, y, h, h)

def aboverect(reference, other):
    return other.bottom < reference.top

def rightofrect(reference, other):
    return other.left > reference.right

def belowrect(reference, other):
    return other.top > reference.bottom

def leftofrect(reference, other):
    return other.right < reference.left

def within_horiz(left, right, rect):
    return not (rect.left > right or rect.right < left)

def within_vert(top, bottom, rect):
    return not (rect.bottom < top or rect.top > bottom)

class nearestrect:

    def __init__(self, refkey, otherkey, comp, extreme):
        self.refkey = refkey
        self.otherkey = otherkey
        self.comp = comp
        self.extreme = extreme

    def __call__(self, reference, rects):
        assert reference not in rects
        reference = pygame.Rect(reference)

        otherattr = op.attrgetter(self.otherkey)
        refattr = op.attrgetter(self.refkey)

        def key(rect):
            return otherattr(pygame.Rect(rect))

        def predicate(other):
            return self.comp(key(other), refattr(reference))

        rects = filter(predicate, rects)
        return self.extreme(rects, key=key, default=None)


nearestabove = nearestrect('top', 'bottom', op.lt, max)
nearestrightof = nearestrect('right', 'left', op.gt, min)
nearestbelow = nearestrect('bottom', 'top', op.lt, min)
nearestleftof = nearestrect('left', 'right', op.lt, max)

nearest_for_side = {
    'top': nearestabove,
    'right': nearestrightof,
    'bottom': nearestbelow,
    'left': nearestleftof,
}

def squircle_shapes(color, center, radius, width, corners):
    """
    Expand a squircle (square+circle) into simpler component shapes.
    """
    filled = width == 0
    x, y = center
    rect = pygame.Rect(x - radius, y - radius, radius*2, radius*2)
    if filled:
        namedrects = dict(zip(pygamelib.CORNERNAMES, rectquadrants(rect)))
        rects = set(namedrects[corner] for corner in corners if filled)
        yield ('ellipse', color, rect, width)
        for r in rects:
            yield ('rect', color, r, width)
    else:
        # compensate for width > 1
        # draw.rect automatically does this
        lines_rect = rect.inflate((-(width-1),)*2)
        lines = set()
        getpoint = functools.partial(getattr, lines_rect)
        for corner in corners:
            attrpairs = pygamelib.CORNERLINES[corner]
            for attrpair in attrpairs:
                lines.add(tuple(map(getpoint, attrpair)))
        # angle pairs in degrees of quadrants to draw
        anticorners = [name for name in pygamelib.CORNERNAMES if name not in corners]
        anglepairs = set(pygamelib.QUADRANT_DEGREES[corner] for corner in anticorners)
        anglepairs = pygamelib.merge_ranges(anglepairs)
        for anglepair in anglepairs:
            angle1, angle2 = map(math.radians, anglepair)
            yield ('arc', color, rect, angle1, angle2, width)
        for line in lines:
            yield ('line', color, *line, width)

class ShapeParser:

    colornames = set(pygame.color.THECOLORS)

    shapenames = set(n for n in dir(pygame.draw) if not n.startswith('_'))
    shapenames.add('squircle')

    def parse_file(self, file):
        for line in file:
            line = line.lstrip()
            if not line or line.startswith('#'):
                continue
            shape = line.split()
            name, color, *remaining = shape
            assert name in self.shapenames
            assert color in self.colornames
            if name == 'arc':
                x, y, w, h, angle1, angle2, width = map(eval, remaining)
                # avoid argument that results in nothing being drawn
                assert width != 0
                angle1, angle2 = map(math.radians, [angle1, angle2])
                yield Arc(color, (x, y, w, h), angle1, angle2, width)
            elif name == 'circle':
                x, y, radius, width = map(eval, remaining)
                yield Circle(color, (x, y), radius, width)
            elif name == 'line':
                x1, y1, x2, y2, width = map(eval, remaining)
                # avoid nothing drawn
                assert width > 0
                yield Line(color, (x1, y1), (x2, y2), width)
            elif name == 'lines':
                closed, width, *points = map(eval, remaining)
                closed = bool(closed)
                # avoid nothing drawn
                assert width > 0
                points = tuple(map(tuple, chunk(points, 2)))
                yield Lines(color, closed, width, points)
            elif name == 'rect':
                x, y, w, h, width, *borderargs = map(eval, remaining)
                yield Rectangle(color, (x, y, w, h), width, *borderargs)
            elif name == 'squircle':
                x, y, radius, width, *corners = remaining
                x, y, radius, width = map(eval, (x, y, radius, width))
                assert all(corner in pygamelib.CORNERNAMES for corner in corners), corners
                yield from pygamelib.squircle_shapes(color, (x, y), radius, width, corners)


class DrawMixin:

    def draw(self, surf, offset=(0,0)):
        self.draw_func(surf, *self.draw_args(offset))


class Use(namedtuple('UseBase', 'href'), DrawMixin):

    def getref(self, shapes):
        for shape in shapes:
            if hasattr(shape, 'id') and shape.id == self.href[:1]:
                return shape


class Circle(
    namedtuple('CircleBase', 'color center radius width id', defaults=[None]),
    DrawMixin,
):
    draw_func = pygame.draw.circle

    def scale(self, scale):
        color, (x, y), radius, width, *rest = self
        return self.__class__(color, (x*scale, y*scale), radius*scale, width*scale, *rest)

    def draw_args(self, offset):
        ox, oy = offset
        color, (x, y), radius, width, *rest = self
        center = (x-ox, y-oy)
        return (color, center, radius, width)


class Rectangle(
    namedtuple(
        'RectangleBase',
        'color rect width'
        # defaults
        ' border_radius'
        ' border_top_left_radius'
        ' border_top_right_radius'
        ' border_bottom_left_radius'
        ' border_bottom_right_radius'
        ' id'
        ,
        defaults = [0, -1, -1, -1, -1, None],
    ),
    DrawMixin
):
    draw_func = pygame.draw.rect

    def scale(self, scale):
        color, rect, width, *borders = self
        rect = tuple(map(lambda v: v*scale, rect))
        # scale borders?
        return self.__class__(color, rect, width*scale, *borders)

    def draw_args(self, offset):
        ox, oy = offset
        color, (x, y, w, h), width, *borders = self
        rect = (x-ox, y-oy, w, h)
        return (color, rect, width, *borders)


class Line(
    namedtuple('LineBase', 'color start end width'),
    DrawMixin,
):
    draw_func = pygame.draw.line

    def scale(self, scale):
        color, (x1, y1), (x2, y2), width = self
        start = (x1*scale, y1*scale)
        end = (x2*scale, y2*scale)
        return self.__class__(color, start, end, width*scale)

    def draw_args(self, offset):
        ox, oy = offset
        color, (x1, y1), (x2, y2), width = self
        start = (x1-ox, y1-oy)
        end = (x2-ox, y2-oy)
        return (color, start, end, width)


class Lines(
    namedtuple('LinesBase', 'color closed width points'),
    DrawMixin,
):
    draw_func = pygame.draw.lines

    def scale(self, scale):
        color, closed, width, points = self
        points = tuple((x*scale, y*scale) for x, y in points)
        return self.__class__(color, closed, width*scale, points)

    def draw_args(self, offset):
        ox, oy = offset
        color, closed, width, points = self
        points = tuple((x-ox, y-oy) for x, y in points)
        return (color, closed, points, width)


class Arc(
    namedtuple('ArcBase', 'color rect angle1 angle2 width'),
    DrawMixin,
):
    draw_func = pygame.draw.arc

    def scale(self, scale):
        color, (x, y, w, h), angle1, angle2, width = self
        rect = (x*scale, y*scale, w*scale, h*scale)
        return self.__class__(color, rect, angle1, angle2, width)

    def draw_args(self, offset):
        ox, oy = offset
        color, (x, y, w, h), angle1, angle2, width = self
        rect = (x-ox, y-oy, w, h)
        return (color, rect, angle1, angle2, width)


def parse_xml(xmlfile):
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    def parse_fill(node):
        fill = child.attrib.get('fill', 'false')
        assert fill in ('true', 'false')
        fill = fill == 'true'
        if fill:
            width = 0
        else:
            # TODO
            width = 1
        return width

    for shape in root.iter('shape'):
        for child in shape.iter():
            if child.tag == 'arc':
                pass
            elif child.tag == 'circle':
                x = int(child.attrib.get('x', '0'))
                y = int(child.attrib.get('y', '0'))
                center = (x, y)
                radius = int(child.attrib.get('radius', '0'))
                color = child.attrib['color']
                width = parse_fill(child)
                yield Circle(color, center, radius, width)
            elif child.tag == 'rect':
                color = child.attrib['color']
                x = int(child.attrib.get('x', '0'))
                y = int(child.attrib.get('y', '0'))
                w = int(child.attrib.get('width', '0'))
                h = int(child.attrib.get('height', '0'))
                width = parse_fill(child)
                border_kwargs = {
                    key: child.attrib[key]
                    for key in Rectangle._field_defaults
                    if key in child.attrib
                }
                yield Rectangle(color, (x, y, w, h), width, **border_kwargs)
            elif child.tag == 'use':
                yield Use(child.attrib['href'])

def command_line_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--display-size',
        type = sizetype(),
        default = '800',
    )
    return parser

def line_line_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    # https://www.jeffreythompson.org/collision-detection/line-line.php
    d = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if d == 0:
        return
    a = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / d
    b = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / d
    if 0 <= a <= 1 and 0 <= b <= 1:
        x = x1 + (a * (x2 - x1))
        y = y1 + (b * (y2 - y1))
        return (x, y)

def orientation(p, q, r):
    """
    Function to find the orientation of triplet (p, q, r).
    The function returns the following values:
    0: Collinear points
    1: Clockwise points
    2: Counterclockwise points
    """
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        # Collinear
        return 0
    elif val > 0:
        # clockwise
        return 1
    else:
        # counterclockwise
        return 2

def find_intersection(p1, q1, p2, q2):
    """
    Function to find the intersection point of two line segments.
    Returns None if the line segments do not intersect.
    """
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if o1 == o2 or o3 == o4:
        # no intersect
        return

    # General case - segments intersect
    # Calculate the intersection point
    det = (q1[0] - p1[0]) * (q2[1] - p2[1]) - (q2[0] - p2[0]) * (q1[1] - p1[1])
    if det == 0:
        # line segments are parallel
        return

    t = ((p2[0] - p1[0]) * (q2[1] - p2[1]) - (p2[1] - p1[1]) * (q2[0] - p2[0])) / det
    intersection_point = (p1[0] + t * (q1[0] - p1[0]), p1[1] + t * (q1[1] - p1[1]))
    return intersection_point

def line_line_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    # works!
    return find_intersection((x1, y1), (x2, y2), (x3, y3), (x4, y4))
