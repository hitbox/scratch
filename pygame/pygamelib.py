import contextlib
import itertools as it
import math
import operator as op
import os
import unittest

# silence and import pygame
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

def wrap(rects):
    tops, rights, bottoms, lefts = zip(*map(sides, rects))
    x = min(lefts)
    y = min(tops)
    right = max(rights)
    bottom = max(bottoms)
    width = right - x
    height = bottom - y
    return (x, y, width, height)

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

interesting_colors_pattern = r'gr[ae]y|white|black|silver|light|medium|dark|\d|red|green|blue'

def interesting_color(color):
    """
    Ignoring alpha, rgb values are not all the same.
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
