import abc
import argparse
import contextlib
import enum
import inspect
import itertools as it
import math
import operator as op
import os
import random
import re
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

class TestModOffset(unittest.TestCase):
    """
    Test modulo with offset.
    """

    def test_modulo_offset(self):
        c = 3
        n = 8
        self.assertEqual(modo(3, n, c), 3)
        self.assertEqual(modo(8, n, c), 3)
        self.assertEqual(modo(9, n, c), 4)
        self.assertEqual(modo(0, n, c), 5)


class TestGroupbyColumns(unittest.TestCase):

    def test_groupby_columns(self):
        pass


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


class TestTouching(unittest.TestCase):

    def test_itertouching_none(self):
        self.assertEqual(
            set(itertouching((0,0,10,10), [(20,20,10,10)])),
            set(),
        )

    def test_itertouching_topbottom(self):
        self.assertEqual(
            set(itertouching((0,0,10,10), [(0,-10,10,10)])),
            {(0,-10,10,10)},
        )

    def test_itertouching_bottomtop(self):
        self.assertEqual(
            set(itertouching((0,0,10,10), [(0,10,10,10)])),
            {(0,10,10,10)},
        )

    def test_itertouching_leftright(self):
        self.assertEqual(
            set(itertouching((0,0,10,10), [(10,0,10,10)])),
            {(10,0,10,10)},
        )

    def test_itertouching_rightleft(self):
        self.assertEqual(
            set(itertouching((0,0,10,10), [(-10,0,10,10)])),
            {(-10,0,10,10)},
        )

    def test_itertouching_complex(self):
        self.assertEqual(
            set(itertouching(
                (0,0,10,10),
                [
                    (-5, 10, 10, 10), # below, right to mid
                    (5, 10, 10, 10), # below, left at mid
                    (10, -5, 10, 10), # above, to right, bottom mid height
                    (10, 5, 10, 10), # right of, top at mid height
                    (20, 20, 10, 10), # not touching
                ]
            )),
            {
                (-5, 10, 10, 10),
                (5, 10, 10, 10),
                (10, -5, 10, 10),
                (10, 5, 10, 10),
            },
        )


class TestFloodRectPair(unittest.TestCase):

    @unittest.expectedFailure
    def test_largest_visible_pair_right_to_left(self):
        self.assertEqual(
            largest_contiguous((0,0,10,10), (10,5,10,10)),
            (0,5,20,5),
        )

    @unittest.expectedFailure
    def test_largest_visible_pair_left_to_right(self):
        self.assertEqual(
            largest_contiguous((0,0,10,10), (-10,5,10,10)),
            (-10,5,20,5),
        )

    @unittest.expectedFailure
    def test_largest_visible_pair_top_to_bottom(self):
        self.assertEqual(
            largest_contiguous((0,0,10,10), (5,-10,10,10)),
            (5,-10,5,20),
        )

    @unittest.expectedFailure
    def test_largest_visible_pair_bottom_to_top(self):
        self.assertEqual(
            largest_contiguous((0,0,10,10), (5,10,10,10)),
            (5,0,5,20),
        )


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


class sizetype:

    def __init__(self, n=2):
        self.n = n

    def __call__(self, string):
        size = tuple(intargs(string))
        while len(size) < self.n:
            size += size
        return size


class eval_type:
    # NOTES
    # - originally specifically designed to evaluate expressions given on the
    #   command line for sorting and filtering colors.
    # - trying to generalize it here
    # - we give keys for the globals/context dict on init

    def __init__(self, name, *keys):
        self.name = name
        self.keys = keys

    def __call__(self, expression_string):
        code = compile(expression_string, self.name, 'eval')
        def code_func(*args):
            context = dict(zip(self.keys, args))
            return eval(code, context)
        return code_func


class EventMethodName:
    """
    Callable to create a method name from a pygame event.
    """

    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, event):
        event_name = pygame.event.event_name(event.type)
        method_name = self.prefix + event_name.lower()
        return method_name


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


class DemoCommand(abc.ABC):

    # optional `command_name` attribute for subparser name

    @staticmethod
    def parser_kwargs():
        """
        New subparser keyword arguments.
        """
        return {}

    @staticmethod
    def add_parser_arguments(parser):
        """
        Add arguments and options here.
        """
        ...


class DemoBase:

    def start(self, engine):
        self.engine = engine
        self.screen = pygame.display.get_surface()
        self.window = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.framerate = 60
        self.elapsed = None
        if not hasattr(self, 'controllers'):
            self.controllers = [self]

    def update(self):
        self.elapsed = self.clock.tick(self.framerate)
        for event in pygame.event.get():
            # handle event with topmost controller
            for i in range(1, len(self.controllers)+1):
                obj = self.controllers[-i]
                handler = get_method_handler(obj, event)
                if handler:
                    handler(event)
                    break


class ShapeBrowser(DemoBase):

    def __init__(self, drawables, styles, offset=None):
        self.drawables = drawables
        self.styles = styles
        assert len(self.drawables) == len(self.styles)
        if offset is None:
            offset = (0,0)
        self.offset = pygame.Vector2(offset)

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            post_quit()

    def do_mousemotion(self, event):
        if event.buttons[0]:
            self.offset += event.rel
            self.draw()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        for drawable, style in zip(self.drawables, self.styles):
            color = style['color']
            width = style['width']
            drawable.draw(self.screen, color, width, self.offset)
        pygame.display.flip()


class SimpleQuitMixin:

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            post_quit()


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


class ColorAttributes(pygame.Color):
    """
    pygame.Color with helpful attributes.
    """

    @property
    def hue(self):
        return self.hsva[0]

    @property
    def saturation(self):
        return self.hsva[1]

    @property
    def value(self):
        return self.hsva[2]

    @property
    def lightness(self):
        return self.hsla[2]


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


class ShapeParser:

    colornames = set(pygame.color.THECOLORS)

    shapenames = set(n for n in dir(pygame.draw) if not n.startswith('_'))
    shapenames.add('squircle')

    # this is messed up
    # the id field was removed from Rectangle
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
                assert all(corner in CORNERNAMES for corner in corners), corners
                yield from squircle_shapes(color, (x, y), radius, width, corners)


class StopMixin:
    """
    Common pattern to stop engine on pygame.QUIT event.
    """

    def do_quit(self, event):
        self.engine.stop()


class QuitKeydownMixin:
    """
    Common pattern to quit on Escape or Q key press.
    """

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            post_quit()


class DrawMixin:

    def draw(self, surf, color, width, offset=(0,0)):
        args = self.draw_args(color, width, offset)
        self.draw_func(surf, *args)


class Animate(
    namedtuple('AnimateBase', 'parent attribute values duration'),
):

    def __repr__(self):
        s = 'Animate('
        if self.parent:
            s += f'{self.parent!r}, '
        s += f'{self.attribute!r}, {self.values!r}, {self.duration!r})'
        return s

    def update(self):
        raise NotImplementedError


class Arc(
    namedtuple('ArcBase', 'rect angle1 angle2'),
    DrawMixin,
):
    draw_func = pygame.draw.arc

    def scale(self, scale):
        color, (x, y, w, h), angle1, angle2 = self
        rect = (x*scale, y*scale, w*scale, h*scale)
        return self.__class__(rect, angle1, angle2)

    def draw_args(self, color, width, offset):
        ox, oy = offset
        (x, y, w, h), angle1, angle2 = self
        rect = (x-ox, y-oy, w, h)
        return (color, rect, angle1, angle2, width)


class Circle(
    namedtuple('CircleBase', 'center radius'),
    DrawMixin,
):
    draw_func = pygame.draw.circle

    def scale(self, scale):
        (x, y), radius, *rest = self
        return self.__class__((x*scale, y*scale), radius*scale, *rest)

    def draw_args(self, color, width, offset):
        ox, oy = offset
        (x, y), radius = self
        center = (x+ox, y+oy)
        return (color, center, radius, width)

    def rect(self):
        (x, y), radius = self
        return (x - radius, y - radius, x + radius * 2, y + radius * 2)

    def create_draw_args(self, time, width):
        angle = mix(time, 0, math.tau)
        rect = self.rect()
        return (rect, 0, angle, width)


class Line(
    namedtuple('LineBase', 'start end'),
    DrawMixin,
):
    draw_func = pygame.draw.line

    def scale(self, scale):
        (x1, y1), (x2, y2) = self
        start = (x1*scale, y1*scale)
        end = (x2*scale, y2*scale)
        return self.__class__(start, end)

    def lerp(self, time):
        (x1, y1), (x2, y2) = self
        return (mix(time, x1, x2), mix(time, y1, y2))

    def slope(self):
        return line_slope(self)

    def draw_args(self, color, width, offset):
        ox, oy = offset
        (x1, y1), (x2, y2) = self
        start = (x1-ox, y1-oy)
        end = (x2-ox, y2-oy)
        return (color, start, end, width)


class Lines(
    namedtuple(
        'LinesBase',
        'closed points animations',
        defaults = (
            None, # animations
        ),
    ),
    DrawMixin,
):
    draw_func = pygame.draw.lines

    def __repr__(self):
        s = f'Lines(closed={self.closed}, points={self.points}'
        if self.animations:
            s += f', {self.animations}'
        s += ')'
        return s

    def scale(self, scale):
        closed, points = self
        points = tuple((x*scale, y*scale) for x, y in points)
        return self.__class__(closed, points)

    def draw_args(self, color, width, offset):
        ox, oy = offset
        points = tuple((x+ox, y+oy) for x, y in self.points)
        return (color, self.closed, points, width)


class Point:
    # NOTES
    # - wanted namedtuple
    # - creating objects from XML, for now, requires adding animations after
    #   the object is created

    def __init__(self, x, y, animations=None):
        self.x = x
        self.y = y
        self.animations = animations


class Polygon(
    namedtuple('PolygonBase', 'points'),
    DrawMixin,
):
    draw_func = pygame.draw.polygon

    def draw_args(self, color, width, offset):
        ox, oy = offset
        points = tuple((x+ox, y+oy) for x, y in self.points)
        return (color, points, width)


class Rectangle(
    namedtuple(
        'RectangleBase',
        'rect'
        # defaults
        ' border_radius'
        ' border_top_left_radius'
        ' border_top_right_radius'
        ' border_bottom_left_radius'
        ' border_bottom_right_radius'
        ,
        defaults = [0, -1, -1, -1, -1],
    ),
    DrawMixin,
):
    draw_func = pygame.draw.rect

    def scale(self, scale):
        rect, *borders = self
        rect = tuple(map(lambda v: v*scale, rect))
        # scale borders?
        return self.__class__(rect, *borders)

    def draw_args(self, color, width, offset):
        ox, oy = offset
        (x, y, w, h), *borders = self
        rect = (x+ox, y+oy, w, h)
        return (color, rect, width, *borders)


class Text(
    namedtuple('TextBase', 'font text rect'),
):

    def draw(self, surf, color, width, offset):
        image = self.font.render(self.text, True, color)
        rect = image.get_rect(topleft=self.rect.topleft)
        rect.topleft += pygame.Vector2(offset)
        surf.blit(image, rect)


class Use(namedtuple('UseBase', 'href'), DrawMixin):
    # TODO
    # - trying to do something like svg <use> tags

    def getref(self, shapes):
        for shape in shapes:
            if hasattr(shape, 'id') and shape.id == self.href[:1]:
                return shape


class RectsGenerator:
    """
    Generate some number of non-overlapping rects.
    """

    def __init__(self, space, n, minwidth, minheight):
        self.space = space
        assert n > 0
        self.n = n
        self.minwidth = minwidth
        self.minheight = minheight
        self.failures = 0
        self.maxfail = None
        self.rects = None
        self.empties = [self.space]
        self.subdivide_stack = None
        self.merge_stack = None

    def reset(self, inside, maxfail=1000):
        self.inside = inside
        self.maxfail = maxfail
        self.rects = []
        self.empties = [inside]
        self.failures = 0

    def is_resolved(self):
        return (
            len(self.rects) == self.n
            and not self.subdivide_stack
            and not self.merge_stack
        )

    def update(self):
        if self.subdivide_stack:
            self.update_subdivide_stack()
        elif self.merge_stack:
            self.update_merge_stack()
        elif len(self.rects) < self.n:
            self.update_random()

    def update_subdivide_stack(self):
        # process one item from stack of pairs of rects to subtract from others
        space, subtract = self.subdivide_stack.pop()
        if not self.subdivide_stack:
            # done subdividing init merging stack
            self.merge_stack = [
                (r1, r2)
                for r1, r2 in it.combinations(self.empties, 2)
                if is_adjacent(r1, r2)
            ]
        self.empties.remove(space)
        self.empties.extend(subtract_rect(space, subtract))

    def update_merge_stack(self):
        # process one pair of rects to merge
        r1, r2 = self.merge_stack.pop()
        if r1 in self.empties:
            self.empties.remove(r1)
        if r2 in self.empties:
            self.empties.remove(r2)
        merged = merge_rects(r1, r2)
        self.empties.append(merged)

    def update_random(self):
        for newrect in self.random_generator():
            self.rects.append(newrect)
            self.subdivide_stack = [
                (empty, newrect)
                for empty in map(pygame.Rect, self.empties)
                if empty.colliderect(newrect)
            ]
            break

    def random_generator(self):
        for empty in map(pygame.Rect, generate_contiguous(self.empties)):
            if empty.width >= self.minwidth and empty.height >= self.minheight:
                while True:
                    x1, y1 = random_point(empty)
                    x2, y2 = random_point(empty)
                    if x1 > x2:
                        x1, x2 = x2, x1
                    if y1 > y2:
                        y1, y2 = y2, y1
                    width = x2 - x1
                    height = y2 - y1
                    if width >= self.minwidth and height >= self.minheight:
                        yield (x1, y1, width, height)
                        break


class TouchingRects(enum.Enum):
    TOP_BOTTOM = enum.auto()
    BOTTOM_TOP = enum.auto()
    LEFT_RIGHT = enum.auto()
    RIGHT_LEFT = enum.auto()


class HeartShape:

    def __init__(self, cleft_angle):
        # the angle from the center of each of the two top quadrant rects
        self.cleft_angle = cleft_angle

    def __call__(self, inside):
        inside = pygame.Rect(inside)
        assert inside.width == inside.height
        quads = map(pygame.Rect, rectquadrants(inside))
        topleft_quad, topright_quad, _, _ = quads
        # top quads need to overlap to make the arcs meet center-top
        radius = topleft_quad.width / 2
        dx = (
            topleft_quad.right
            - (
                topleft_quad.centerx
                + math.cos(math.radians(self.cleft_angle))
                * radius
            )
        )
        topleft_quad.move_ip(+dx, 0)
        topright_quad.move_ip(-dx, 0)

        yield Arc(
            rect = topleft_quad,
            angle1 = math.radians(self.cleft_angle),
            angle2 = math.radians(self.cleft_angle+180),
        )
        yield Arc(
            rect = topright_quad,
            angle1 = math.radians(-self.cleft_angle),
            angle2 = math.radians(-self.cleft_angle+180),
        )
        # points where the heart becomes straight lines to the pointy bottom
        p1 = (
            pygame.Vector2(topleft_quad.center)
            + circle_point(math.radians(self.cleft_angle+180), radius)
        )
        p2 = (
            pygame.Vector2(topright_quad.center)
            + circle_point(math.radians(-self.cleft_angle), radius)
        )
        slope_tangent1 = circle_slope_tangent(topleft_quad.center, p1)
        slope_tangent2 = circle_slope_tangent(topright_quad.center, p2)
        x, y = intersection_point(p1, -slope_tangent1, p2, -slope_tangent2)

        # pointy bottom part
        yield Lines(closed=False, points=[p1, (x,y), p2])


class Meter:
    # may be better just described as a range of integer values inclusive

    def __init__(self, value=0, maxvalue=10, minvalue=0):
        self.value = value
        self.maxvalue = maxvalue
        self.minvalue = minvalue
        assert self.minvalue < self.maxvalue

    @property
    def nticks(self):
        return self.maxvalue - self.minvalue

    def slots(self):
        slot = self.minvalue
        while slot <= self.maxvalue:
            # value of the slot, whether that slot is filled
            yield (slot, slot <= self.value)
            slot += 1


class SimpleMeterRender:

    def __init__(self, meter, rect, style=None):
        self.meter = meter
        self.rect = pygame.Rect(rect)
        if style is None:
            style = dict()
        self.style = style

    def draw(self, surf, color, width, offset):
        # TODO:better-draw-signature
        # - work out a better function signature
        # - probably just make the rects for this meter and somehow associate a
        #   style with each rect
        # - need to style based if the meter segment is filled
        if 'color' not in self.style:
            return
        color_on = self.style['color']
        color_off = self.style.get('segment_color_off', 'grey')

        margin = self.style.get('segment_margin', 0)
        margin_top, margin_right, margin_bottom, margin_left = expand_shorthand(margin)

        # line width or fill
        width = self.style.get('segment_width', 0)
        border = self.style.get('segment_border', 0)
        nticks = self.meter.nticks

        tick_width = (
                self.rect.width - (nticks - 1) * (margin_left + margin_right)
            ) // nticks

        items = enumerate(range(self.meter.minvalue, self.meter.maxvalue))
        for i, slotval in items:
            rect = (
                self.rect.x + i * (tick_width + margin_left),
                self.rect.y + margin_top,
                tick_width,
                self.rect.height - margin_bottom * 2
            )
            if slotval < self.meter.value:
                color = color_on
            else:
                color = color_off
            pygame.draw.rect(surf, color, rect, width)


class CircularMeterRenderer:

    def __init__(
        self,
        meter,
        center,
        outer_radius,
        segment_offset,
        inner_radius = 0,
        start_angle = 0,
        end_angle = 360,
        style = None,
    ):
        self.meter = meter
        self.center = center
        self.outer_radius = outer_radius
        self.segment_offset = segment_offset
        self.inner_radius = inner_radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        if style is None:
            style = dict()
        self.style = style

    def draw(self, surf, color, width, offset):
        # TODO:better-draw-signature
        if 'segment_color' not in self.style:
            return

        color_on = self.style['segment_color']
        color_off = self.style.get('segment_color_off', 'grey')
        width = self.style.get('segment_width', 0)
        segment_border_width = self.style.get('segment_border_width')
        segment_border_color = self.style.get('segment_border_color')

        nticks = self.meter.nticks
        radii = (self.outer_radius, self.inner_radius)
        segment_angle_step = (self.end_angle - self.start_angle) // nticks
        # there's overdraw of points here, a problem? necessary?
        angle = self.start_angle
        for slotval, slotfilled in self.meter.slots():
            points = circle_segment_points(
                (
                    math.radians(angle - self.segment_offset),
                    math.radians(angle + self.segment_offset),
                ),
                radii,
                closed = True,
            )
            points = [pygame.Vector2(self.center) + point for point in points]
            if slotfilled:
                color = color_on
            else:
                color = color_off
            pygame.draw.polygon(surf, color, points, width)
            if segment_border_color:
                # draw a border for circle segment
                pygame.draw.polygon(
                    surf,
                    segment_border_color,
                    points,
                    segment_border_width
                )
            angle += segment_angle_step


class BorderStyle(
    namedtuple(
        'BorderStyle',
        'width color',
        defaults = ('magenta',)
    ),
):

    @classmethod
    def from_shorthand(cls, string):
        items = zip([int, pygame.Color], string.split())
        args = (func(arg) for func, arg in items)
        return cls(*args)


class SpriteSheet(
    namedtuple(
        'SpriteSheet',
        'image width height scale',
        defaults = (-1, -1, 1),
    )
):
    """
    :param image:
    :param width: slice width
    :param height: slice height
    :param scale: scale after slicing
    """
    # XXX
    # - too much in this class
    # - probably want a separate "ImageSlicer" class

    help = (
        'path/to/image.ext width=-1 height=-1 scale=1.'
        ' Negative slice dimensions use image dimension.'
    )

    @classmethod
    def from_shorthand(cls, string):
        items = zip([pygame.image.load, int, int, int], string.split())
        args = (func(arg) for func, arg in items)
        return cls(*args)

    def get_images(self):
        image_width, image_height = self.image.get_size()
        width = self.width
        height = self.height
        if width < 0:
            width = image_width
        if height < 0:
            height = image_height
        width = min(width, image_width)
        height = min(height, image_height)
        return sliceimage(self.image, (width, height))


def scale(factor, image):
    # - partial-able function
    size = pygame.Vector2(image.get_size()) * factor
    return pygame.transform.scale(image, size)

def sliceimage(image, size):
    width, height = size
    image_width, image_height = image.get_size()
    for x in range(0, image_width, width):
        for y in range(0, image_height, height):
            yield image.subsurface(x, y, width, height)

# shape producing

def step_for_radius(radius):
    # NOTE
    # - this is the step between start and end angle
    # - smaller number is more segments
    # TODO
    # dialing in n radian steps for good enough looking circles made of lines.
    if radius >= 300:
        return 2
    else:
        return 8

def circle_segment_points1(angle, offset, radii, closed=False):
    """
    :param angle:
        Used with offset to get two angles either side of this one.
    :param offset:
        Circle segment width either side of angle.
    :param radii:
        Two-tuple of outer and inner radius.
    """
    # TODO
    # - two angle what could be used to make star shapes
    # - that, or two offsets--the outer one being zero
    inner_radius, outer_radius = radii

    lesser_angle = angle - offset
    greater_angle = angle + offset

    # two points, straight line from outer to inner radii
    first = circle_point(lesser_angle, outer_radius)
    yield first
    yield circle_point(lesser_angle, inner_radius)

    step = math.radians(step_for_radius(inner_radius))
    while lesser_angle < angle + offset:
        yield circle_point(lesser_angle, inner_radius)
        lesser_angle += step

    # straight line from inner to outer
    yield circle_point(greater_angle, inner_radius)
    yield circle_point(greater_angle, outer_radius)

    step = math.radians(step_for_radius(outer_radius))
    while greater_angle > angle - offset:
        yield circle_point(greater_angle, outer_radius)
        greater_angle -= step

    if closed:
        yield first

def circle_segment_points(angles, radii, closed=False):
    lesser_angle, greater_angle = angles
    inner_radius, outer_radius = radii

    # two points, straight line from outer to inner radii
    first = circle_point(lesser_angle, outer_radius)
    yield first
    yield circle_point(lesser_angle, inner_radius)

    step = math.radians(step_for_radius(inner_radius))
    while lesser_angle < angles[1]:
        yield circle_point(lesser_angle, inner_radius)
        lesser_angle += step

    # straight line from inner to outer
    yield circle_point(greater_angle, inner_radius)
    yield circle_point(greater_angle, outer_radius)

    step = math.radians(step_for_radius(outer_radius))
    while greater_angle > angles[0]:
        yield circle_point(greater_angle, outer_radius)
        greater_angle -= step

    if closed:
        yield first

# engine

def run(state):
    engine = Engine()
    engine.run(state)

# events

def get_method_handler(obj, event):
    method_name = default_methodname(event)
    method = getattr(obj, method_name, None)
    return method

def dispatch(obj, event):
    method = get_method_handler(obj, event)
    if method is not None:
        method(event)

def _post(event_type):
    pygame.event.post(pygame.event.Event(event_type))

def post_quit():
    _post(pygame.QUIT)

def post_videoexpose():
    _post(pygame.VIDEOEXPOSE)

# general purpose

class TestSnakeCaseFunction(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(snake_case('PascalCase'), 'pascal_case')

    def test_underscore_in_pascal(self):
        # not sure what to do if underscores are in pascal case
        with self.assertRaises(ValueError):
            snake_case('Pascal_Case')

    def test_weird(self):
        self.assertEqual(snake_case('PC'), 'pc')
        # leave runs of caps alone
        self.assertEqual(snake_case('XML'), 'xml')

    def test_todo_fix_loses_parts(self):
        # FIXME
        # - loses the XML part
        self.assertEqual(snake_case('XMLShapes'), 'shapes')


pascal_case_re = re.compile(r'[A-Z][a-z]+')

def snake_case(name):
    if '_' in name:
        raise ValueError('Underscore in name')
    matches = list(pascal_case_re.finditer(name))
    if not matches:
        return name.lower()
    return '_'.join(match.group().lower() for match in matches)

def batched(iterable, n):
    """
    group items in iterable into n-length tuples
    """
    iterable = iter(iterable)
    while batch := tuple(it.islice(iterable, n)):
        yield batch

def range_with_end(start, stop, step):
    r = range(start, stop, step)
    for value in r:
        yield value
    if len(r) > 0 and value != stop:
        yield stop

def range_with_end_float(start, stop, step):
    if step < 0:
        loop_cmp = op.gt
        final_cmp = op.le
    else:
        loop_cmp = op.lt
        final_cmp = op.ge
    while loop_cmp(start, stop):
        yield start
        start += step
    if final_cmp(start, stop):
        yield stop

def ranges_overlap(start1, stop1, start2, stop2):
    return (
        start2 <= start1 <= stop2
        or start2 <= stop1 <= stop2
        or start1 <= start2 <= stop1
        or start1 <= stop2 <= stop1
    )

def expand_shorthand(value):
    if isinstance(value, (float, int)):
        value = [value]
    value = list(value)
    n = len(value)
    if n == 1:
        top, right, bottom, left = value * 4
    elif n == 2:
        top, right, bottom, left = value * 2
    elif n == 3:
        top, right, bottom = value
        left = right
    else:
        top, right, bottom, left = value
    return (top, right, bottom, left)

def nwise(iterable, n=2, fill=None):
    "Take from iterable in `n`-wise tuples."
    iterables = it.tee(iterable, n)
    # advance iterables for offsets
    for offset, iterable in enumerate(iterables):
        # advance with for-loop to avoid catching StopIteration manually.
        for _ in zip(range(offset), iterable):
            pass
    return it.zip_longest(*iterables, fillvalue=fill)

def sorted_groupby(iterable, key=None, reverse=False):
    """
    Convenience for sorting and then grouping.
    """
    return it.groupby(sorted(iterable, key=key, reverse=reverse), key=key)

def intargs(string):
    return map(int, string.replace(',', ' ').split())

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

def steppairs(start, stop, step):
    # steppairs(0, 360, 30) -> (0, 30), (30, 60), ..., (330, 360)
    for i in range(start, stop, step):
        yield (i, i+step)

def floatrange(start, stop, step):
    while start < stop:
        yield start
        start += step

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

def modo(a, b, offset):
    """
    modulo offset, returns a % b shifted for offset.
    """
    return offset + ((a - offset) % (b - offset))

def clamp(x, a, b):
    if x < a:
        return a
    elif x > b:
        return b
    return x

def mix(time, a, b):
    """
    Return the value between a and b at time.
    """
    return a * (1 - time) + b * time

lerp = mix

# TODO
# - lerp a string? sounds kinda neat.

def remap(x, a, b, c, d):
    """
    Return x from range a and b to range c and d.
    """
    return x*(d-c)/(b-a) + c-a*(d-c)/(b-a)

def remap_rect(rect1, p, rect2):
    """
    remap x,y position from rect1 to a position in rect2
    """
    # TODO
    # - cleaner more consistent
    x, y = p
    r1x = (rect1.left, rect1.right)
    r2x = (rect2.left, rect2.right)
    r1y = (rect1.top, rect1.bottom)
    r2y = (rect2.top, rect2.bottom)
    return (remap(x, *r1x, *r2x), remap(y, *r1y, *r2y))

# color

def get_color(arg, **kwargs):
    """
    Set attributes on a color while instantiating it.
    Example:

    get_color('red', a=255//2)
    For getting 'red' and setting the alpha at the same time.
    """
    # kind of like get_rect
    color = pygame.Color(arg)
    for key, val in kwargs.items():
        setattr(color, key, val)
    return color

def color_name(color):
    color = pygame.Color(color)
    return UNIQUE_COLORSTHE[tuple(color)]

# command line

def rect_type(string):
    """
    pygame Rect arguments as from command line or text file.
    """
    return pygame.Rect(*intargs(string))

def circle_type(string):
    x, y, radius = intargs(string)
    return ((x, y), radius)

def add_display_size_option(parser, **kwargs):
    kwargs.setdefault('type', sizetype())
    kwargs.setdefault('default', '800')
    kwargs.setdefault(
        'help',
        'Display size. %(default)s'
    )
    parser.add_argument('--display-size', **kwargs)

def command_line_parser(**kwargs):
    parser = argparse.ArgumentParser(**kwargs)
    add_display_size_option(parser)
    add_framerate_option(parser)
    return parser

def add_framerate_option(parser, name='--framerate', **kwargs):
    kwargs.setdefault('type', int)
    kwargs.setdefault('default', 60)
    parser.add_argument(name, **kwargs)

def add_null_separator_flag(parser, **kwargs):
    kwargs.setdefault('action', 'store_true')
    kwargs.setdefault('help', 'Separate rects with null.')
    parser.add_argument('-0', **kwargs)

def add_dimension_separator_option(parser, **kwargs):
    kwargs.setdefault('default', ' ')
    kwargs.setdefault('help', 'Rect dimensions separator.')
    parser.add_argument('-d', '--dimsep', **kwargs)

def add_point_arguments(parser, name, **kwargs):
    kwargs.setdefault('help', 'One or more point arguments.')
    parser.add_argument(name, nargs='+', type=sizetype())

def format_pipe(iterable, null_separator, dimsep):
    """
    :param iterable: iterable of iterables
    """
    # fairly purpose built for rects
    if null_separator:
        end = '\0'
    else:
        end = '\n'
    return end.join(dimsep.join(map(str, item)) for item in iterable)

def print_pipe(pipe_string, null_separator, file=None):
    print(pipe_string, end='', file=file)
    if not null_separator:
        # print newline for line separated
        print(file=file)

def add_animate_option(parser, **kwargs):
    """
    Add option taking five positional arguments:
    1. name
    2. start value
    3. end value
    4. start time
    5. end time
    """
    # NOTES
    # - holding off enforcing here, that the values and times are int or float
    #   because who knows?
    argnames = ('NAME', 'START_VALUE', 'END_VALUE', 'START_TIME', 'END_TIME')
    kwargs.setdefault('nargs', len(argnames))
    kwargs.setdefault('metavar', argnames)
    kwargs.setdefault('action', 'append')
    parser.add_argument('--animate', **kwargs)

def animation_tuple(value, end_value=None, start_time=0, end_time=0):
    """
    Return a tuple meant to be inside a container for animations with default
    values so that everything can be treated like an animation, even if it is
    not changing.
    """
    if end_value is None:
        end_value = value
    return ((value, end_value), (start_time, end_time))

def variables_from_animations(animations, time):
    """
    Generate animation key/values for given time.
    """
    for name, (values, times) in animations.items():
        start_time, end_time = times
        if time < start_time or time > end_time or end_time == 0:
            # outside time range or avoid division by zero
            value = values[0]
        else:
            value = mix((time - start_time) / end_time, *values)
        yield (name, value)

def update_variables_from_animations(animations, variables, time):
    for name, ((value1, value2), times) in animations.items():
        start_time, end_time = times
        if start_time <= time <= end_time:
            time = (time - start_time) / end_time
            value = mix(time, value1, value2)
            variables[name] = value

def is_demo_command(obj):
    return (
        inspect.isclass(obj)
        and issubclass(obj, DemoCommand)
        and obj is not DemoCommand
    )

def iterdemos(objects):
    return filter(is_demo_command, objects)

def get_subcommand_name(demo_class):
    if hasattr(demo_class, 'command_name'):
        name = demo_class.command_name
    else:
        name = snake_case(demo_class.__name__)
    return name

# rects

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

def opposite_items(indexable):
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
        rect = EMPTY_RECT
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
    tops, rights, bottoms, lefts = zip(*map(extremities, rects))
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
    for r1, r2 in it.combinations(map(pygame.Rect, rects), 2):
        clipping = r1.clip(r2)
        if clipping:
            yield (r1, r2, clipping)

def side_lines(rect):
    rect = pygame.Rect(rect)
    yield (rect.topleft, rect.topright)
    yield (rect.topright, rect.bottomright)
    yield (rect.bottomright, rect.bottomleft)
    yield (rect.bottomleft, rect.topleft)

def corners(rect):
    x, y, w, h = rect
    # topleft
    yield (x, y)
    # topright
    yield (x + w, y)
    # bottomright
    yield (x + w, y + h)
    # bottomleft
    yield (x, y + h)

def sides(rect):
    """
    Scalar values of the sides of a rect in anticlockwise order from the top.
    """
    # NOTE: avoid relying on pygame.Rect attributes
    left, top, w, h = rect
    right = left + w
    bottom = top + h
    return (top, right, bottom, left)

def named_sides(rect):
    return zip(SIDENAMES, sides(rect))

def side_lines(rect):
    left, top, width, height = rect
    right = left + width
    bottom = top + height
    # lines in clockwise order
    # top line
    yield ((left, top), (right, top))
    # right line
    yield ((right, top), (right, bottom))
    # bottom line
    yield ((right, bottom), (left, bottom))
    # left line
    yield ((left, bottom), (left, top))

def top(rect):
    _, top, _, _ = rect
    return top

def right(rect):
    x, _, w, _ = rect
    return x + w

def bottom(rect):
    _, y, _, h = rect
    return y + h

def left(rect):
    left, _, _, _ = rect
    return left

def best_name_colors(color_items):
    # NOTES
    # - pygame.color.THECOLORS has many names for some colors
    # - for instance 'grey100', 'gray100', and 'white' are all white.
    # - also 'red' and 'red1' are the same.
    # Here, we group color items by the tuple value and yield the hightest
    # quality name.
    second = op.itemgetter(1)
    grouped = sorted_groupby(color_items, key=second)

    def _quality(color_item):
        # count of digits in key
        key, val = color_item
        return len(set(key).intersection(string.digits))

    for _, color_items in grouped:
        color_items = sorted(color_items, key=_quality)
        yield color_items[0]

def flow_leftright(rects, gap=0):
    for r1, r2 in it.pairwise(rects):
        r2.left = r1.right + gap

def flow_topbottom(rects, gap=0):
    for r1, r2 in it.pairwise(rects):
        r2.top = r1.bottom + gap

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

def system_font(name, size, bold=False, italic=False):
    # init is very cheap and this removes a pain point
    # timeit: 10000000 loops, best of 5: 24.1 nsec per loop
    pygame.font.init()
    return pygame.font.SysFont(name, size, bold, italic)

def monospace_font(size, bold=False, italic=False):
    return system_font('monospace', size, bold, italic)

def render_text(
    font,
    size,
    background,
    color,
    text,
    text_shade = 'black',
    shade = 0.5,
    antialias = True,
    attr = 'center',
):
    """
    Render `color` colored `text` aligned onto an image of `size` filled with
    `background`.

    :param font: pygame font to render text.
    :param size: size of final image.
    :param background: background fill color.
    :param color: color of text.
    :param text: text to render with font.
    :param text_shade: color lerped toward background to shade for text.
    :param shade: fraction for lerp.
    :param antialias: antialias font.
    :param attr: attribute align text onto background.
    """
    background = pygame.Color(background)
    result_image = pygame.Surface(size)
    result_image.fill(background)
    result_rect = result_image.get_rect()
    label_shade = background.lerp(text_shade, shade)
    text_image = font.render(text, antialias, color, label_shade)
    text_kw = {attr: getattr(result_rect, attr)}
    text_rect = text_image.get_rect(**text_kw)
    result_image.blit(text_image, text_rect)
    return result_image

def circle_rect(center, radius):
    """
    Wrap a circle in a rect
    """
    x, y = center
    return (x-radius, y-radius, radius*2, radius*2)

def circle_surface(
    radius,
    color,
    surface_flags = pygame.SRCALPHA,
    circle_width = 0,
):
    """
    Create a surface and draw a circle on it.
    """
    surface = pygame.Surface((radius*2,)*2, surface_flags)
    pygame.draw.circle(surface, color, (radius,)*2, radius, circle_width)
    return surface

def centered_offset(rects, window):
    """
    Offset vector for a window rect centered on a group of rects.
    """
    if not isinstance(window, pygame.Rect):
        # assume it is a size
        window = pygame.Rect((0,)*2, window)
    rect = pygame.Rect(wrap(rects))
    rect.center = window.center
    return pygame.Vector2(rect.topleft)

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

def is_adjacent(rect1, rect2):
    l1, t1, w1, h1 = rect1
    l2, t2, w2, h2 = rect2
    r1 = l1 + w1
    b1 = t1 + h1
    r2 = l2 + w2
    b2 = t2 + h2
    return (
        (w1 == w2 and l1 == l2 and (t1 == b2 or t2 == b1))
        or
        (h1 == h2 and t1 == t2 and (l1 == r2 or l2 == r1))
    )

def merge_rects(rect1, rect2):
    l1, t1, w1, h1 = rect1
    l2, t2, w2, h2 = rect2
    r1 = l1 + w1
    b1 = t1 + h1
    r2 = l2 + w2
    b2 = t2 + h2
    if w1 == w2 and l1 == l2 and (t1 == b2 or t2 == b1):
        # same width, same left and sharing top/bottom
        return (l1, min(t1, t2), w1, h1 + h2)
    elif h1 == h2 and t1 == t2 and (l1 == r2 or l2 == r1):
        # same height, same top and sharing left/right
        return (min(l1, l2), t1, w1 + w2, h1)

def has_mergeable(rects):
    for rect1, rect2 in it.combinations(rects, 2):
        if merge_rects(rect1, rect2):
            return True

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
    """
    Generate rects of a rect's four quadrants.
    """
    x, y, w, h = rect
    hw = w / 2
    hh = h / 2
    # topleft
    yield (x, y, hw, hh)
    # topright
    yield (x + hw, y, hw, hh)
    # bottomright
    yield (x + hw, hh, hw, hh)
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

def rect_handles_border(rect, width, margin=0):
    """
    Generate handles on a rect like Gimp.
    """
    x, y, w, h = rect
    r = x + w
    b = y + h
    half = width / 2
    # topleft
    yield (x - half, y - half, width, width)
    # top
    yield (x + half + margin, y - half, w - width - margin * 2, width)
    # topright
    yield (r - half, y - half, width, width)
    # right
    yield (r - half, y + half + margin, width, h - width - margin * 2)
    # bottomright
    yield (r - half, b - half, width, width)
    # bottom
    yield (x + half + margin, b - half, w - width - margin * 2, width)
    # bottomleft
    yield (x - half, b - half, width, width)
    # left
    yield (x - half, y + half + margin, width, h - width - margin * 2)

def rect_handles_outside(rect, width):
    """
    Generate handles on a rect like Gimp.
    """
    x, y, w, h = rect
    r = x + w
    b = y + h
    half = width / 2
    # topleft
    yield (x - width, y - width, width, width)
    # top
    yield (x, y - width, w, width)
    # topright
    yield (r, y - width, width, width)
    # right
    yield (r, y, width, h)
    # bottomright
    yield (r, b, width, width)
    # bottom
    yield (x, b, w, width)
    # bottomleft
    yield (x - width, b, width, width)
    # left
    yield (x - width, y, width, h)

def move_handle(rect, width):
    x, y, w, h = rect
    cx = x + w // 2
    cy = y + h // 2
    half = width // 2
    return (cx - half, cy - half, width, width)

def update_handle(rect, name, rel):
    rx, ry = rel
    rw = rx
    rh = ry
    if 'left' in name:
        # compensate for width
        rw = -rw
    if 'top' in name:
        # compensate for height
        rh = -rh
    if 'right' in name:
        # lock x
        rx = 0
    if 'bottom' in name:
        # lock y
        ry = 0
    rect.x += rx
    rect.y += ry
    rect.width += rw
    rect.height += rh

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

def squircle_shapes(color, center, radius, width, corners):
    """
    Expand a squircle (square+circle) into simpler component shapes.
    """
    filled = width == 0
    x, y = center
    rect = pygame.Rect(x - radius, y - radius, radius*2, radius*2)
    if filled:
        namedrects = dict(zip(CORNERNAMES, rectquadrants(rect)))
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
            attrpairs = CORNERLINES[corner]
            for attrpair in attrpairs:
                lines.add(tuple(map(getpoint, attrpair)))
        # angle pairs in degrees of quadrants to draw
        anticorners = [name for name in CORNERNAMES if name not in corners]
        anglepairs = set(QUADRANT_DEGREES[corner] for corner in anticorners)
        anglepairs = merge_ranges(anglepairs)
        for anglepair in anglepairs:
            angle1, angle2 = map(math.radians, anglepair)
            yield ('arc', color, rect, angle1, angle2, width)
        for line in lines:
            yield ('line', color, *line, width)

def line_rect_intersections(line, rect):
    for rectline in side_lines(rect):
        intersection = line_line_intersection(line, rectline)
        if intersection:
            yield intersection

def line_line_intersection1(x1, y1, x2, y2, x3, y3, x4, y4):
    # https://www.jeffreythompson.org/collision-detection/line-line.php
    # TODO
    # - duplicates of line/line intersection funcs
    # - which to keep
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

def line_line_intersection2(x1, y1, x2, y2, x3, y3, x4, y4):
    # works!
    return find_intersection((x1, y1), (x2, y2), (x3, y3), (x4, y4))

def line_line_intersection(line1, line2):
    line1p1, line1p2 = line1
    line2p1, line2p2 = line2
    return find_intersection(line1p1, line1p2, line2p1, line2p2)

def line_midpoint(p1, p2):
    p1 = pygame.Vector2(p1)
    p2 = pygame.Vector2(p2)
    return p1 + (p2 - p1) / 2

def flatten_line(line):
    p1, p2 = line
    return (*p1, *p2)

def flatten_lines(*lines):
    return tuple(flatten_line(line) for line in lines)

def random_point(rect):
    l, t, w, h = rect
    r = l + w
    b = t + h
    x = random.randint(l, r)
    y = random.randint(t, b)
    return (x, y)

def random_rect(inside):
    l, t, w, h = inside
    r = l + w
    b = t + h
    x1 = random.randint(l, r)
    y1 = random.randint(t, b)
    x2 = random.randint(l, r)
    y2 = random.randint(t, b)
    # NOTE
    # - check and flip fastest in benchmarks
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    return (x1, y1, x2 - x1, y2 - y1)

def random_rect_from_empties(empties):
    if len(empties) < 2:
        return random_rect(empties[0])

    # using choice so that the same empty may be selected
    #empty1, empty2 = random.sample(empties, 2)
    empty1 = random.choice(empties)
    empty2 = random.choice(empties)
    x1, y1 = random_point(empty1)
    x2, y2 = random_point(empty2)
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    return (x1, y1, x2 - x1, y2 - y1)

def subtract_rect(space, rect_to_subtract):
    """
    Subdivide `space` by `rect_to_subtract`.
    """
    space = pygame.Rect(space)
    clip = space.clip(rect_to_subtract)
    if not clip:
        # no intersection
        yield space
    else:
        if space.left < clip.left:
            # left rect
            width = clip.left - space.left
            height = space.height
            yield (space.left, space.top, width, height)
        if space.right > clip.right:
            # right rect
            width = space.right - clip.right
            height = space.height
            yield (clip.right, space.top, width, height)
        if space.top < clip.top:
            # top rect including left- and right-top
            minright = min(space.right, clip.right)
            maxleft = max(space.left, clip.left)
            width = minright - maxleft
            height = clip.top - space.top
            yield (maxleft, space.top, width, height)
        if space.bottom > clip.bottom:
            # bottom rect including left- and right-bottom
            minright = min(space.right, clip.right)
            maxleft = max(space.left, clip.left)
            width = minright - maxleft
            height = space.bottom - clip.bottom
            yield (maxleft, clip.bottom, width, height)

def subtract_rect_from_all(empties, rect_to_subtract):
    """
    Subdivide all the rects in empties by rect_to_subtract.
    """
    for empty in empties:
        for rect in subtract_rect(empty, rect_to_subtract):
            yield rect

def find_empty_space(rects, inside):
    """
    Subdivide the `inside` rect by all rects and return a list of rects
    representing the negative space.
    """
    empties = [inside]
    for rect in rects:
        empties = list(subtract_rect_from_all(empties, rect))
    return empties

def extremities(rect):
    """
    Clockwise sides of rect starting from top.
    """
    left, top, width, height = rect
    right = left + width
    bottom = top + height
    return (top, right, bottom, left)

def is_touching(rect1, rect2):
    rect1left, rect1top, rect1width, rect1width = rect1
    rect1right = rect1left + rect1width
    rect1bottom = rect1top + rect1width
    rect2left, rect2top, rect2width, rect2width = rect2
    rect2right = rect2left + rect2width
    rect2bottom = rect2top + rect2width
    if rect1left < rect2right and rect1right > rect2left:
        # within horizontal
        if rect1top == rect2bottom:
            return TouchingRects.TOP_BOTTOM
        elif rect1bottom == rect2top:
            return TouchingRects.BOTTOM_TOP
    elif rect1top < rect2bottom and rect1bottom > rect2top:
        # within vertical
        if rect1left == rect2right:
            return TouchingRects.LEFT_RIGHT
        elif rect1right == rect2left:
            return TouchingRects.RIGHT_LEFT

def touch_relation(rect1, rect2):
    """
    If rects touch, return a tuple describing the touching relationship.
    """
    top1, right1, bottom1, left1 = extremities(rect1)
    top2, right2, bottom2, left2 = extremities(rect2)
    if ranges_overlap(left1, right1, left2, right2):
        if top1 == bottom2:
            return (('top', 'bottom'), top1)
        elif top2 == bottom1:
            return (('top', 'bottom'), top2)
    if ranges_overlap(top1, bottom1, top2, bottom2):
        if right1 == left2:
            return (('right', 'left'), right1)
        elif right2 == left1:
            return (('right', 'left'), right2)

def itertouching(rect, others):
    rectleft, recttop, rectwidth, rectheight = rect
    rectright = rectleft + rectwidth
    rectbottom = recttop + rectheight

    def recurse(other):
        rest = set(map(tuple, others))
        rest.remove(tuple(other))
        return itertouching(other, rest)

    for other in others:
        otherleft, othertop, otherwidth, otherheight = other
        otherright = otherleft + otherwidth
        otherbottom = othertop + otherheight
        if is_touching(rect, other):
            yield other
            yield from recurse(other)

def largest_contiguous(rect1, rect2):
    """
    Largest contiguous space inside touching rects.
    """
    touching = is_touching(rect1, rect2)
    if not touching:
        return rect1
    left, top, right, bottom = extremities(rect1)
    if touching == TouchingRects.RIGHT_LEFT:
        _, top2, right, bottom2 = extremities(rect2)
        top = max(top, top2)
        bottom = min(bottom, bottom2)
    elif touching == TouchingRects.LEFT_RIGHT:
        left, top2, _, bottom2 = extremities(rect2)
        top = max(top, top2)
        bottom = min(bottom, bottom2)
    elif touching == TouchingRects.TOP_BOTTOM:
        left2, top, right2, _ = extremities(rect2)
        left = max(left, left2)
        right = min(right, right2)
    elif touching == TouchingRects.BOTTOM_TOP:
        left2, _, right2, bottom = extremities(rect2)
        left = max(left, left2)
        right = min(right, right2)
    return (left, top, right - left, bottom - top)

def generate_contiguous(rects):
    rects = list(map(pygame.Rect, rects))
    tops, rights, bottoms, lefts = zip(*map(extremities, rects))
    bounding = (min(lefts), min(tops), max(rights) - min(lefts), max(bottoms) - min(tops))
    negative_space = list(map(pygame.Rect, find_empty_space(rects, bounding)))
    generated = set()
    for top, right, bottom, left in it.product(tops, rights, bottoms, lefts):
        if left > right:
            left, right = right, left
        if top > bottom:
            top, bottom = bottom, top

        width = right - left
        height = bottom - top
        # ignore zero dimensions
        if width == 0 or height == 0:
            continue

        # corners is not part of any existing rect
        # ignore if none of the corners are part of an existing rect
        corners = (
            (left, top),
            (right-1, top),
            (right-1, bottom-1),
            (left, bottom-1),
        )
        if not any(rect.collidepoint(corner) for rect in rects for corner in corners):
            continue

        # TODO
        # - clean up
        # - probably use sets more
        # - probably less checks
        # - going away to see about grouping rects into islands--rects that are touching

        newrect = (left, top, width, height)
        # avoid duplicates
        if newrect in generated or newrect in rects:
            continue
        # ignore new rect that collides with negative space
        if any(negative.colliderect(newrect) for negative in negative_space):
            continue

        yield newrect
        generated.add(newrect)

def minmax(iterable):
    return (min(iterable), max(iterable))

def bounding_rect(coords):
    axes = zip(*coords)
    (x, y), (right, bottom) = zip(*(map(minmax, axes)))
    width = right - x
    height = bottom - y
    return (x, y, width, height)

def reduce_rect(rect, f):
    _, _, width, height = rect
    if isinstance(f, (float, int)):
        f = (f, ) * 2
    args = map(lambda a, b: a * b, (width, height), f)
    return rect.inflate(*args)

def line_slope(line):
    (x1, y1), (x2, y2) = line
    return (y2 - y1) / (x2 - x1)

def perpendicular_line_segments(line, n, length):
    (x1, y1), (x2, y2) = line
    slope = line_slope(line)
    perpendicular_slope = -1 / slope
    for time in map(lambda i: i / n, range(n+1)):
        px = mix(time, x1, x2)
        py = mix(time, y1, y2)
        delta_x = length  / (1 + perpendicular_slope ** 2) ** 0.5
        delta_y = perpendicular_slope * delta_x
        x3 = px + delta_x
        y3 = py + delta_y
        x4 = px - delta_x
        y4 = py - delta_y
        yield ((x3, y3), (x4, y4))

def line_segments_polygons(lines):
    for line1, line2 in it.pairwise(lines):
        line1p1, line1p2 = line1
        line2p1, line2p2 = line2
        yield [
            line1p1,
            line2p1,
            line2p2,
            line1p2,
        ]

def circle_point(angle, radius):
    """
    Screen-space point on a circle.
    """
    return (+math.cos(angle) * radius, -math.sin(angle) * radius)

def circle_pointsf(start, stop, step, radius):
    # would guess there is much more error using floatrange
    # because adds compound errors instead of calculating radians each time
    for angle in floatrange(start, stop, step):
        x = +math.cos(angle) * radius
        y = -math.sin(angle) * radius
        yield (x, y)

def circle_points(degrees, radius):
    for angle in map(math.radians, degrees):
        x = +math.cos(angle) * radius
        y = -math.sin(angle) * radius
        yield (x, y)

def circle_slope_tangent(center, point):
    cx, cy = center
    x, y = point
    derivative_x = 2 * (x - cx)
    derivative_y = 2 * (y - cy)
    slope = derivative_x / derivative_y
    return slope

def rect_diagonal_lines(rect, steps, reverse=False, clip=False):
    """
    Generate the lines for drawing that caution zone looking diagonal lines
    from a rect.
    """
    left, top, width, height = rect
    _, rightline, bottomline, leftline = side_lines(rect)
    stepx, stepy = steps
    assert stepx > 1 and stepy > 1
    right = left + width
    bottom = top + height
    if reverse:
        x1s = range(right, left - height, -stepx)
        x2s = it.repeat(right)
    else:
        x1s = range(left, right + width, stepx)
        x2s = it.repeat(left)
    y1s = it.repeat(top)
    y2s = it.count(top, stepy)
    for x1, y1, x2, y2 in zip(x1s, y1s, x2s, y2s):
        line = ((x1, y1), (x2, y2))
        if clip:
            if reverse:
                if x1 < left:
                    x1, y1 = line_line_intersection(line, leftline)
            else:
                if x1 > right:
                    x1, y1 = line_line_intersection(line, rightline)
            if y2 > bottom:
                x2, y2 = line_line_intersection(line, bottomline)
        yield ((x1, y1), (x2, y2))

def intersection_point(point1, slope1, point2, slope2):
    # Check if the slopes are equal (parallel lines)
    if slope1 == slope2:
        return None  # Lines are parallel, no intersection

    x1, y1 = point1
    x2, y2 = point2

    # Calculate the x-coordinate of the intersection point
    intersection_x = (slope2 * x2 - y2 - slope1 * x1 + y1) / (slope2 - slope1)

    # Calculate the y-coordinate using either line equation
    intersection_y = slope1 * (intersection_x - x1) + y1

    return intersection_x, intersection_y

def bezier(control_points, t):
    degree = len(control_points) - 1
    position = pygame.Vector2()
    for index, point in enumerate(control_points):
        coefficient = math.comb(degree, index) * (1-t)**(degree-index) * t**index
        position += point * coefficient
    return position

def cubic_bezier(p0, p1, p2, p3, t):
    """
    Return position on cubic bezier curve at time t.
    """
    one_minus_t = 1 - t
    # (1 - t) ** 3
    b0 = one_minus_t * one_minus_t * one_minus_t
    # 3 * (1 - t) ** 2
    b1 = 3 * (one_minus_t * one_minus_t)
    # 3 * (1 - t) * t ** 2
    b2 = 3 * one_minus_t * (t * t)
    # t ** 3
    b3 = t * t * t
    # NOTE: unpacking is slower than getitem indexing
    x = b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0]
    y = b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1]
    return (x, y)

def cubic_bezier_derivative(p0, p1, p2, p3, t):
    one_minus_t = 1 - t
    # -3 * (1 - t) ** 2
    b0 = -3 * (one_minus_t * one_minus_t)
    # 3 * (1 - t) ** 2 - 6 * (1 - t) * t
    b1 = 3 * (one_minus_t * one_minus_t) - 6 * one_minus_t * t
    # 6 * (1 - t) * t -3 * t ** 2
    b2 = 6 * one_minus_t * t - 3 * (t * t)
    # 3 * t ** 2
    b3 = 3 * (t * t)
    dx = b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0]
    dy = b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1]
    return (dx, dy)

def bezier_tangent(control_points, t):
    # rewrite of above
    degree = len(control_points) - 1
    delta = pygame.Vector2()
    for index, (p1, p2) in enumerate(it.pairwise(control_points)):
        coefficient = (
            (degree * (p2 - p1))
            *
            math.comb(degree-1, index)
            *
            (1 - t)**(degree-1-index) * t**index
        )
        delta += coefficient
    return delta

def bernstein_poly(i, degree, t):
    """
    Bernstein polynomial for index i, degree n, evaluated at t.
    """
    return math.comb(degree, i) * (t ** i) * ((1 - t) ** (degree - i))

def bezier_curve(control_points, t):
    """
    Compute the point on the Bézier curve for parameter t.

    :param control_points: List of control points [(x0, y0), (x1, y1), ..., (xn, yn)]
    :param t: Parameter value, ranging from 0 to 1
    :return: Point on the curve at parameter t
    """
    n = len(control_points)
    degree = n - 1
    x = sum(bernstein_poly(i, degree, t) * control_points[i][0] for i in range(n))
    y = sum(bernstein_poly(i, degree, t) * control_points[i][1] for i in range(n))
    return (x, y)

def bezier_curve_points(control_points, steps):
    for i in range(steps+1):
        yield bezier_curve(control_points, i/steps)

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

getxy = op.itemgetter('x', 'y')

def shape_from_element(element, parent=None):
    shape = None
    if element.tag == 'lines':
        closed = element.attrib.get('closed', False)
        # child <point> elements required
        points_elements = element.findall('points')
        assert len(points_elements) == 1
        points = list(shape_from_element(points_elements[0]))
        shape = Lines(closed, points)

    elif element.tag == 'points':
        shape = tuple(map(shape_from_element, element.findall('point')))

    elif element.tag == 'point':
        shape = Point(*map(int, getxy(element.attrib)))

    elif element.tag == 'animate':
        # NOTES
        # - animate is not a shape
        # - should it be an attribute of the object?
        # - should it be an attribute of the object's attribute?
        shape = Animate(
            parent,
            element.attrib['attribute'],
            element.attrib['values'],
            element.attrib['duration'],
        )

    if shape is not None:
        animate_elements = element.findall('animate')
        if animate_elements:
            shape.animations = []
            for animate_element in animate_elements:
                animate = shape_from_element(animate_element, parent=shape)
                shape.animations.append(animate)
        return shape

class Shapes:

    def __init__(self, database, shapes):
        self.database = database
        self.shapes = shapes

    @classmethod
    def from_xml(cls, root):
        database = {}
        shapes = []
        for element in root.iter():
            shape = shape_from_element(element)
            if shape:
                if 'id' in element.attrib:
                    shape_id = element.attrib['id']
                    assert shape_id not in database
                    database[shape_id] = shape
                shapes.append(shape)
        return cls(database, shapes)


def points_from_file(file):
    """
    Load points from text file supporting comments.
    """
    # probably not going to continue this function
    # want to do animations on shapes and things
    # do NOT want to write my own parsing
    # probably going xml
    for line in file:
        line = line.strip()
        if not line:
            continue
        if '#' in line:
            if line.strip().startswith('#'):
                continue
            line = line[:line.index('#')]
        line = line.replace(',', ' ')
        yield tuple(map(int, line.split()))

def lerp_rect(rect, time):
    """
    Return point on rect border at time.
    """
    # TODO
    # - arbitrary starting corner
    topleft, topright, bottomright, bottomleft = corners(rect)
    if time < 0.25:
        start = topleft
        end = topright
    elif time < 0.50:
        start = topright
        end = bottomright
    elif time < 0.75:
        start = bottomright
        end = bottomleft
    else:
        start = bottomleft
        end = topleft
    # NOTES
    # - trouble getting my head around modulo .25 and then divide by .25
    # - modulo to put the time in the range of one of the sides
    # - division because there are four sides
    # - division to scale time to that side
    time = (time % 0.25) / 0.25
    return mix(time, pygame.Vector2(start), pygame.Vector2(end))

SIDE_ENDS = [0.25, 0.50, 0.75, 1.00]

def lerp_rect_lines(rect, start, end):
    """
    Generate the lines needed to get from a point on the border of a rect at
    start time to end time.
    """
    p1 = lerp_rect(rect, start)
    # TODO
    # - is this good? indexing for end of side and having to modulo for
    #   protection
    side1 = int(start / 0.25) % len(SIDE_ENDS)
    side2 = int(end / 0.25) % len(SIDE_ENDS)
    if side1 == side2:
        # base case and done
        yield (p1, lerp_rect(rect, end))
    else:
        endtime1 = SIDE_ENDS[side1]
        yield (p1, lerp_rect(rect, endtime1))
        yield from lerp_rect_lines(rect, endtime1, end)

def trace_rect(rect, time):
    """
    Generate lines along border of rect at time.
    """
    topleft, topright, bottomright, bottomleft = corners(rect)
    if time < 0.25:
        start = topleft
    elif time < 0.50:
        yield (topleft, topright)
        start = topright
    elif time < 0.75:
        yield (topleft, topright)
        yield (topright, bottomright)
        start = bottomright
    else:
        yield (topleft, topright)
        yield (topright, bottomright)
        yield (bottomright, bottomleft)
        start = bottomleft
    yield (start, lerp_rect(rect, time))

def trace_circle(time):
    return mix(time, 0, math.tau)

def cubic_ease_in_out(time):
    # NOTES
    # - unsure about these constants but I put them into desmos and they come
    #   out between 0 and 1
    return time * time * time * (time * (6 * time - 15) + 10)

# clockwise ordered rect side attribute names mapped with their opposites
SIDENAMES = ['top', 'right', 'bottom', 'left']
SIDES = dict(opposite_items(SIDENAMES))

# clockwise ordered rect point attribute names mapped with their opposites
POINTS = dict(opposite_items(tuple(point_attrs(tuple(SIDES)))))

EMPTY_RECT = pygame.Rect((0,)*4)

CORNERNAMES = ['topleft', 'topright', 'bottomright', 'bottomleft']

HANDLE_NAMES = [
    'topleft',
    'top',
    'topright',
    'right',
    'bottomright',
    'bottom',
    'bottomleft',
    'left',
]

# counter-clockwise degrees
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

UNIQUE_THECOLORS = dict(best_name_colors(pygame.color.THECOLORS.items()))
UNIQUE_COLORSTHE = {v: k for k, v in UNIQUE_THECOLORS.items()}

default_methodname = EventMethodName(prefix='do_')

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

# rect with no effect on wrap
NORECT = (math.inf, math.inf, -math.inf, -math.inf)

DELTAS = set(tuple(v-1 for v in divmod(i, 3)) for i in range(9))
DELTAS.remove((0,0))
