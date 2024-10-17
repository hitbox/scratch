import abc
import argparse
import contextlib
import enum
import fileinput
import functools
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

from collections import defaultdict
from collections import namedtuple

# silently import pygame
with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

# clean up namespace
del contextlib
del os

DEFAULT_DISPLAY_SIZE = (800, 800)
DEFAULT_DISPLAY_WIDTH, DEFAULT_DISPLAY_HEIGHT = DEFAULT_DISPLAY_SIZE

FILL = 0

class TestItemized(unittest.TestCase):
    """
    Test wrapping version of nwise.
    """

    def test_itemized(self):
        expected = [(1,2,3), (2,3,4), (3,4,5), (4,5,1), (5,1,2)]

        result = []
        i = 0
        for thing in itemized(range(5), 3):
            print(thing)
            result.append(thing)
            i += 1
            if i > 9:
                break
        #result = list(itemized(range(5), 3))
        self.assertEqual(expected, result)


class Timer:

    def __init__(self, start, duration, end_stop=None):
        self.start = start
        self.duration = duration
        if end_stop is None:
            end_stop = 1
        self.end_stop = end_stop
        self.end = None
        self.time = 0
        self.start_count = 0
        self.end_count = 0

    def is_running(self):
        return self.end_count < self.start_count

    def is_stopped(self):
        return self.end_count == self.start_count

    def should_start(self):
        return self.end_count < self.end_stop and self.time >= self.start

    def should_end(self):
        return self.end and self.time >= self.end

    def update(self, elapsed):
        self.time += elapsed
        if self.is_running():
            if self.should_end():
                self.end_count += 1
        elif self.should_start():
            self.start_count += 1
            if self.end_count > 0:
                # repeating, advance start by duration
                self.start += self.duration
            self.end = self.start + self.duration

    def normtime(self):
        return (self.time - self.start) / self.duration


class FontRenderer:

    def __init__(self, font, color, antialias=True, background=None):
        self.font = font
        self.color = color
        self.antialias = antialias
        self.background = background

    def __call__(self, string, antialias=None, color=None, background=None):
        if antialias is None:
            antialias = self.antialias
        if color is None:
            color = self.color
        if background is None:
            background = self.background
        return self.font.render(string, antialias, color, background)


class FontPrinter:
    """
    Callable renders like print() from pygame font.
    """

    def __init__(self, font, color=None, antialias=True):
        self.font = font
        self.color = color
        self.antialias = antialias

    def __call__(self, lines, color=None):
        """
        Render lines from top to bottom into an image.
        """
        color = color or self.color
        args = (lines, self.font, color, self.antialias)
        images, rects = make_blitables_from_font(*args)
        _, _, w, h = wrap(rects)
        result = pygame.Surface((w, h), pygame.SRCALPHA)
        result.blits(zip(images, rects))
        return result


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
            for obj in self.controllers[::-1]:
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

    @property
    def rgba(self):
        return (self.r, self.g, self.b, self.a)

    @property
    def rgb(self):
        return self.rgba[:3]

    @property
    def red(self):
        return self.r

    @property
    def green(self):
        return self.g

    @property
    def blue(self):
        return self.b


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

    def render(self, surf, color, width, offset):
        ox, oy = offset
        (x, y, w, h), angle1, angle2 = self
        rect = pygame.Rect(x-ox, y-oy, w, h)

        image = pygame.Surface(rect.size, pygame.SRCALPHA)
        self.draw_func(image, color, ((0,0), rect.size), angle1, angle2, width)
        return surf.blit(image, rect)


class Circle(
    namedtuple('CircleBase', 'center radius'),
    DrawMixin,
):
    draw_func = pygame.draw.circle

    @classmethod
    def from_arg(cls, string):
        center, radius = circle_type(string)
        return cls(center, radius)

    def collides(self, other):
        return circle_collision(self, other)

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

    @classmethod
    def from_arg(cls, string):
        string = string.strip()
        if string:
            x, y, w, h = simple_rect_type(string.strip())
            return cls((x, y, w, h))

    @property
    def size(self):
        (x, y, w, h), *_ = self
        return (w, h)

    def render_onto(self, surf, color, width, offset):
        # XXX
        # - janky method for rendering rects with alpha in color for adhoc use
        #   with polygon_wrap
        ox, oy = offset
        (x, y, w, h), *_ = self
        image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(image, color, (0, 0, w, h), width)
        return surf.blit(image, (x + ox, y + oy))

    @property
    def ltrb(self):
        (x, y, w, h), *_ = self
        r = x + w
        b = y + h
        return (x, y, r, b)

    @property
    def points(self):
        l, t, r, b = self.ltrb
        # topleft, topright, bottomright, bottomleft
        yield (l, t)
        yield (r, t)
        yield (r, b)
        yield (l, b)

    @property
    def lines(self):
        l, t, r, b = self.ltrb
        yield ((l, t), (r, t))
        yield ((r, t), (r, b))
        yield ((r, b), (l, b))
        yield ((l, b), (l, t))

    def intersections(self, other):
        self_rect, *_ = self
        other_rect, *_ = other
        self_horizontal, self_vertical = oriented_side_lines(self_rect)
        other_horizontal, other_vertical = oriented_side_lines(other_rect)

        line_pairs = [
            (self_horizontal, other_vertical),
            (self_vertical, other_horizontal),
        ]

        for self_line, other_line in line_pairs:
            for linepair in it.product(self_line, other_line):
                point = line_line_intersection(*linepair)
                if point:
                    yield point

    def collides(self, other):
        return rect_collision(self, other)

    def clip(self, other):
        return rect_clip(self, other)

    def contains_point(self, point):
        # point collides without being one of our corners
        rect, *_ = self
        x, y, w, h = rect
        r = x + w
        b = y + h
        # TODO
        # - check also not on side/edge line?
        if point not in ((x,y), (r,y), (r,b), (x,b)):
            return pygame.Rect(rect).collidepoint(point)

    def contains_line(self, line):
        rect, *_ = self
        x, y, w, h = rect
        r = x + w
        b = y + h
        rect = pygame.Rect(rect)
        mx, my = line_midpoint(line)
        return x < mx < r and y < my < b

    def collide_point(self, point):
        rect, *_ = self
        return pygame.Rect(rect).collidepoint(point)

    def inside_point(self, point):
        px, py = point
        rect, *_ = self
        x, y, w, h = rect
        r = x + w
        b = y + h
        if pygame.Rect(rect).collidepoint(point):
            # could be corner or on edge
            return px not in (x, r) and py not in (y, b)

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
        return self.from_rect(inside)

    @classmethod
    def instance_from_rect(cls, cleft_angle, inside):
        inst = cls(cleft_angle)
        # TODO:
        # - consume to update instance
        # - fix decision to make a generator
        list(inst.from_rect(inside))
        return inst

    def draw(self, surf, color, width, offset=(0,0)):
        self.topleft_arc.draw(surf, color, width, offset)
        self.topright_arc.draw(surf, color, width, offset)
        self.pointy.draw(surf, color, width, offset)

    def from_rect(self, inside):
        inside = pygame.Rect(inside)
        self.inside = inside
        # TODO: why must equal?
        #assert inside.width == inside.height
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

        self.topleft_arc = Arc(
            rect = topleft_quad,
            angle1 = math.radians(self.cleft_angle),
            angle2 = math.radians(self.cleft_angle+180),
        )
        yield self.topleft_arc

        self.topright_arc = Arc(
            rect = topright_quad,
            angle1 = math.radians(-self.cleft_angle),
            angle2 = math.radians(-self.cleft_angle+180),
        )
        yield self.topright_arc
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
        self.pointy = Lines(closed=False, points=[p1, (x,y), p2])
        yield self.pointy


class HeartShape2:

    def __init__(self, cleft_angle, inside=None):
        """
        :param cleft_angle:
            angle in degrees of middletop cleft in heart shape. 45 degrees is a
            good choice.
        """
        self.cleft_angle = cleft_angle
        if inside:
            self.update(inside)

    def update(self, inside):
        self.inside = pygame.Rect(inside)
        quads = map(pygame.Rect, rectquadrants(self.inside))

        self.topleft_quad, self.topright_quad, _, _ = quads
        # top quads need to overlap to make the arcs meet center-top
        self.arc_radius = self.topleft_quad.width / 2
        width_delta = (
            self.topleft_quad.right
            - (
                self.topleft_quad.centerx
                + math.cos(math.radians(self.cleft_angle))
                * self.arc_radius
            )
        )
        self.topleft_quad.width += width_delta
        self.topleft_quad.left = self.inside.left

        self.topleft_arc = Arc(
            rect = self.topleft_quad,
            angle1 = math.radians(self.cleft_angle),
            angle2 = math.radians(self.cleft_angle+180),
        )

        self.topright_quad.width += width_delta
        self.topright_quad.right = self.inside.right

        self.topright_arc = Arc(
            rect = self.topright_quad,
            angle1 = math.radians(-self.cleft_angle),
            angle2 = math.radians(-self.cleft_angle+180),
        )

        # points where the heart becomes straight lines to the pointy bottom
        p1 = (
            pygame.Vector2(self.topleft_quad.center)
            + circle_point(
                -math.radians(self.cleft_angle+180),
                self.arc_radius
            )
        )
        p2 = (
            pygame.Vector2(self.topright_quad.center)
            + circle_point(
                -math.radians(-self.cleft_angle),
                self.arc_radius
            )
        )
        slope_tangent1 = circle_slope_tangent(self.topleft_quad.center, p1)
        slope_tangent2 = circle_slope_tangent(self.topright_quad.center, p2)
        bottom_point = intersection_point(p1, -slope_tangent1, p2, -slope_tangent2)

        # pointy bottom part
        self.pointy = Lines(closed=False, points=[p1, bottom_point, p2])

    def draw(self, surf, color, width, offset=(0,0), debug_color=None):
        """
        :param debug_color:
            enables debugging draws and sets color
        """
        if debug_color:
            render_rect(surf, debug_color, self.topleft_quad, 1)
            render_rect(surf, debug_color, self.topright_quad, 1)

            real_topleft_quad, *_ = map(pygame.Rect, rectquadrants(self.inside))

            p1 = real_topleft_quad.center
            p2 = (
                p1[0] + math.cos(self.cleft_angle) * self.arc_radius,
                p1[1] + -math.sin(self.cleft_angle) * self.arc_radius,
            )
            pygame.draw.line(surf, debug_color, p1, p2, 1)

        self.topleft_arc.render(surf, color, width, offset)
        self.topright_arc.render(surf, color, width, offset)
        self.pointy.draw(surf, color, width, offset)


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
        'width colorarg',
        defaults = ('magenta',)
    ),
):
    # XXX
    # - namedtuple won't let me have _color
    # - colorarg is my compromise

    @classmethod
    def from_shorthand(cls, string):
        items = zip([int, str], string.split())
        args = (func(arg) for func, arg in items)
        return cls(*args)

    @property
    def color(self):
        return pygame.Color(self.colorarg)

    @property
    def shorthand(self):
        color = get_color_name(self.colorarg)
        if isinstance(color, (pygame.Color, tuple)):
            color = ''.join(color)
        return f'{self.width} {color}'


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


class RectRenderer:
    # XXX
    # - separate "structure" from style?

    def __init__(
        self,
        color,
        width = 0,
        border_radius = 0,
        border_top_left_radius = -1,
        border_top_right_radius = -1,
        border_bottom_left_radius = -1,
        border_bottom_right_radius = -1,
    ):
        self.color = color
        self.width = width
        self.border_radius = border_radius
        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius

    def draw_kwargs(self):
        return dict(
            width = self.width,
            border_radius = self.border_radius,
            border_top_left_radius = self.border_top_left_radius,
            border_top_right_radius = self.border_top_right_radius,
            border_bottom_left_radius = self.border_bottom_left_radius,
            border_bottom_right_radius = self.border_bottom_right_radius,
        )

    def __call__(self, surf, rect):
        if isinstance(self.color, (list, tuple)):
            for (p1, p2), color in zip(side_lines(rect), self.color):
                pygame.draw.line(surf, color, p1, p2) # TODO other args
        else:
            return pygame.draw.rect(surf, self.color, rect, **self.draw_kwargs())


class StackedRectRenderer:

    def __init__(self, rect_renderers):
        self.rect_renderers = rect_renderers

    def __call__(self, surf, rect):
        for renderer in self.rect_renderers:
            renderer(surf, rect)


class rect_type:

    def __init__(self, with_pygame=False):
        self.with_pygame = with_pygame

    def __call__(self, string):
        if self.with_pygame:
            container = pygame.Rect
        else:
            container = tuple
        x, y, w, h = intargs(string)
        return container((x, y, w, h))


class rects_type_or_stdin:
    # XXX
    # - this does not work
    # - want to take rects as stdin pipe or arguments

    def __init__(self):
        self.rects = []

    def __call__(self, string):
        if string == '-':
            # this is roughly what argparse.FileType.__call__ does
            for line in fileinput.input():
                self.rects.append(simple_rect_type(line))
        else:
            self.rects.append(simple_rect_type(string))


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

def elementwise(f, *iterables):
    return map(f, *iterables)

def angle_to(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

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
    # XXX
    # - remove?
    # - don't remember using this
    # - really, a whole function to do this?
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

def frange(start, stop=None, step=None):
    if stop is None:
        stop = start
        start = 0.0

    if step is None:
        step = 1.0

    current = float(start)

    def within_range(current, stop, step):
        if step > 0:
            return current < stop
        else:
            return current > stop

    while within_range(current, stop, step):
        yield current
        current += step

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
    """
    Take from iterable in `n`-wise tuples.
    """
    # TODO
    # - add wrapping? (1, 2, 3) -> (1, 2), (2, 3), (3, 1). use the fill value?
    iterables = it.tee(iterable, n)
    # advance iterables for offsets
    for offset, iterable in enumerate(iterables):
        # advance with for-loop to avoid catching StopIteration manually.
        for _ in zip(range(offset), iterable):
            pass
    return it.zip_longest(*iterables, fillvalue=fill)

def advance(iterator, n=1):
    # use while to let StopIteration raise
    i = 0
    while i < n:
        next(iterator)
        i += 1
    return iterator

def itemized(iterable, n=2):
    # NOTES
    # - is it worth all this, to be compatible with generators and the like?
    # - whereas a list is easy

    # three-wise
    # (1,2,3,4,5)
    #   -> (1,2,3), (2,3,4), (3,4,5), (4,5,1), (5,1,2)
    # no need for all this machinery if wrapping won't occur
    assert n > 1

    iterables = it.tee(iterable, n)

    # TODO
    # need to replace index < n with repeat

    for offset, iterable in enumerate(iterables):
        for _ in range(offset):
            next(iterable)

    def wrapped_iterable(i, iterator):
        print(i, iterator, n)
        if i < n:
            # repeat forever for wrapping
            return it.repeat(iterator)
        else:
            # advance by index
            return advance(iterator, i)

    iterables = map(wrapped_iterable, it.count(), it.tee(iterable, n))
    return zip(*iterables)

def sorted_groupby(iterable, key=None, reverse=False):
    """
    Convenience for sorting and then grouping.
    """
    return it.groupby(sorted(iterable, key=key, reverse=reverse), key=key)

def splitarg(string):
    return string.replace(',', ' ').split()

def intargs(string):
    return map(int, splitarg(string))

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

def segmented_lerp(points, time, closed=False):
    if closed:
        points += [points[0]]

    lengths = [math.dist(p1, p2) for p1, p2 in zip(points, points[1:])]
    total_length = sum(lengths)

    travelled = time * total_length

    accumulated_length = 0
    for i, length in enumerate(lengths):
        if accumulated_length + length >= travelled:
            segment_t = (travelled - accumulated_length) / length
            p1 = points[i+0]
            p2 = points[i+1]
            x = lerp(segment_t, p1[0], p2[0])
            y = lerp(segment_t, p1[1], p2[1])
            return (x, y)

        accumulated_length += length

    return points[-1]

def inverse_lerp(a, b, p):
    return (p - a) / (b - a)

def inverse_lerp(a, b, p):
    ab = b - a  # Vector from a to b
    ap = p - a  # Vector from a to p

    # Calculate the length of the projection of ap onto ab
    ab_length_squared = ab.length_squared()
    if ab_length_squared == 0:
        raise ValueError("The points a and b must be different for interpolation.")

    # Use dot product to find the projection of ap onto ab
    t = ap.dot(ab) / ab_length_squared
    return t

def mixiters(time, iter1, iter2):
    return tuple(mix(time, a, b) for a, b in zip(iter1, iter2))

def mixangle_longest(a, b, time):
    # lerp between angles, the longest way around
    longest_distance = math.tau - abs(a - b)
    return (a + longest_distance * time) % math.tau

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

def get_color_name(color):
    key = tuple(pygame.Color(color))
    return UNIQUE_COLORSTHE.get(key, color)

def random_colorfuls(n):
    # XXX
    # - maybe too much here
    # - mainly needed to generate more colors than pygame defines
    colorfuls = map(pygame.Color, UNIQUE_COLORSTHE_COLORFUL)
    colorfuls = it.cycle(colorfuls)
    colorfuls = tuple(it.islice(colorfuls, n))
    colorfuls = random.sample(colorfuls, n)
    return colorfuls

# command line

def repeat_type(s):
    """
    Value for Timer.repeat from command line.
    """
    if s == 'inf':
        return math.inf
    return int(s)

point_type = sizetype()

def simple_rect_type(string):
    """
    pygame Rect arguments as from command line or text file.
    """
    return tuple(intargs(string))

def knife_type(s):
    """
    One to four space or comma separated integer for a rect:
    x, y, w, h.
    """
    # 100 -> 0, 0, 100, 100
    # 100, 200 -> 0, 0, 100, 200
    # 10, 20, 100 -> 10, 20, 100, 100
    # 10, 20, 100, 200 -> 10, 20, 100, 200
    # XXX
    # - want to put additional help text for argument somewhere
    values = tuple(map(int, s.replace(',', ' ').split()))
    n = len(values)
    x = y = 0
    if n == 1:
        w = h = values
    elif n == 2:
        w, h = values
    elif n == 3:
        x, y, w = values
        h = w
    elif n == 4:
        x, y, w, h = values
    else:
        raise ValueError
    return (x, y, w, h)

def circle_type(string):
    x, y, radius = intargs(string)
    return ((x, y), radius)

def add_display_size_option(parser, **kwargs):
    kwargs.setdefault('type', sizetype())
    kwargs.setdefault(
        'default',
        f'{DEFAULT_DISPLAY_WIDTH},{DEFAULT_DISPLAY_HEIGHT}',
    )
    kwargs.setdefault(
        'help',
        'Display size. %(default)s'
    )
    parser.add_argument('--display-size', **kwargs)

def command_line_parser(**kwargs):
    parser = argparse.ArgumentParser(**kwargs)
    add_display_size_option(parser)
    add_framerate_option(parser)
    add_background_color_option(parser)
    return parser

def add_background_color_option(parser, name='--background', **kwargs):
    kwargs.setdefault('type', pygame.Color)
    kwargs.setdefault('default', 'black')
    kwargs.setdefault('help', 'Background color.')
    parser.add_argument(name, **kwargs)

def add_framerate_option(parser, name='--framerate', **kwargs):
    kwargs.setdefault('type', int)
    kwargs.setdefault('default', 0)
    kwargs.setdefault('help', 'Frames per second.')
    parser.add_argument(name, **kwargs)

def add_null_separator_flag(parser, **kwargs):
    kwargs.setdefault('action', 'store_true')
    kwargs.setdefault('dest', 'null')
    kwargs.setdefault('help', f'Separate with null.')
    parser.add_argument('-0', **kwargs)

def add_dimension_separator_option(parser, **kwargs):
    kwargs.setdefault('default', ' ')
    kwargs.setdefault('help', 'Dimensions separator.')
    parser.add_argument('-d', '--dimsep', **kwargs)

def add_point_arguments(parser, name, **kwargs):
    kwargs.setdefault('help', 'One or more point arguments.')
    parser.add_argument(name, nargs='+', type=sizetype())

def add_seed_option(parser, name='--seed', **kwargs):
    kwargs.setdefault('type', random.seed)
    parser.add_argument(name, **kwargs)

def add_rects_argument(parser, name='rects', **kwargs):
    kwargs.setdefault('type', simple_rect_type)
    parser.add_argument(name, **kwargs)

def add_shapes_from_file_arguments(
    parser,
    name = 'shapes',
    shape_choices = None,
    **kwargs,
):
    """
    Add two required arguments
    """
    if shape_choices is None:
        # TODO
        # - probably more discipline here
        shape_choices = ['circle', 'rect']

    kwargs.setdefault('type', argparse.FileType('r'))
    kwargs.setdefault('help', 'Read shapes from file including stdin.')
    parser.add_argument(name, **kwargs)

    parser.add_argument('shape_type', choices=shape_choices)

def add_number_option(parser, name='-n', subject=None, **kwargs):
    if subject is None:
        subject = 'things'
    kwargs.setdefault('type', int)
    kwargs.setdefault('default', 1)
    kwargs.setdefault('help', f'Number of {subject}. Default: %(default)s')
    parser.add_argument(name, **kwargs)

def shapes_from_args(args):
    if args.shape_type == 'circle':
        type_ = Circle.from_arg
    elif args.shape_type == 'rect':
        type_ = Rectangle.from_arg
    for shape_string in map(str.strip, args.shapes):
        if not shape_string.startswith('#'):
            shape = type_(shape_string)
            if shape:
                yield shape

def format_pipe(iterable, null_separator, dimsep):
    """
    :param iterable: iterable of items
    """
    # fairly purpose built for rects
    if null_separator:
        end = '\0'
    else:
        end = '\n'
    return end.join(dimsep.join(map(str, item)) for item in iterable)

def print_pipe(string, null_separator, file=None):
    """
    Print string for piping.
    """
    if string:
        print(string, end='', file=file)
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

def stop_repeat():
    pygame.key.set_repeat(0)

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
    rect = pygame.Rect(rect).copy()
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

def with_rect(surf, **kwargs):
    # this seems to happen a lot
    return (surf, surf.get_rect(**kwargs))

def wrap(rects):
    # NOTES
    # - wrapping only makes sense against an iterable of rects
    top, right, bottom, left = extremities(*rects)
    return (top, left, right - left, bottom - top)

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
    return rect[2] * rect[3]

def overlaps(rects):
    for r1, r2 in it.combinations(map(pygame.Rect, rects), 2):
        clipping = r1.clip(r2)
        if clipping:
            yield (r1, r2, clipping)

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

def topline(rect):
    x, y, w, h = rect
    return ((x, y), (x + w, y))

def rightline(rect):
    x, y, w, h = rect
    r = x + w
    return ((r, y), (r, y + h))

def bottomline(rect):
    # NOTE
    # - clockwise orientation
    x, y, w, h = rect
    b = y + h
    return ((x + w, b), (x, b))

def leftline(rect):
    # NOTE
    # - clockwise orientation
    x, y, w, h = rect
    return ((x, y + h), (x, y))

def side_lines(rect):
    x, y, w, h = rect
    r = x + w
    b = y + h
    yield ((x, y), (r, y))
    yield ((r, y), (r, b))
    yield ((x, b), (r, b))
    yield ((x, y), (x, b))

def hlines(rect):
    x, y, w, h = rect
    r = x + w
    b = y + h
    yield ((x, y), (r, y))
    yield ((x, b), (r, b))

def vlines(rect):
    x, y, w, h = rect
    r = x + w
    b = y + h
    yield ((x, y), (x, b))
    yield ((r, y), (r, b))

def oriented_side_lines(rect):
    top, right, bottom, left = side_lines(rect)
    yield (top, bottom)
    yield (left, right)

def corners(rect):
    x, y, w, h = rect
    r = x + w
    b = y + h
    # topleft
    yield (x, y)
    # topright
    yield (r, y)
    # bottomright
    yield (r, b)
    # bottomleft
    yield (x, b)

points = corners

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

def ccw_side_lines(rect):
    left, top, width, height = rect
    right = left + width
    bottom = top + height
    # top line
    yield ((right, top), (left, top))
    # left line
    yield ((left, top), (left, bottom))
    # bottom line
    yield ((left, bottom), (right, bottom))
    # right line
    yield ((right, bottom), (right, top))

def side_lines_from_point(rect, point):
    sides = list(side_lines(rect))
    for i in range(4):
        if point_on_line_segment(sides[i], point):
            break
    for i in range(i, i+4):
        yield sides[i % 4]

def ccw_corners(rect):
    x, y, w, h = rect
    r = x + w
    b = y + h
    # topleft
    yield (x, y)
    # bottomleft
    yield (x, b)
    # bottomright
    yield (r, b)
    # topright
    yield (r, y)

def find_line_for_point(rect, point):
    px, py = point
    for p1, p2 in it.pairwise(corners(rect)):
        x1, y1 = p1
        x2, y2 = p2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y1:
            y1, y2 = y2, y1
        if (
            # point lies inside horizontal line p1-p2
            (y1 == y2 == py and x1 < px < x2)
            or
            # point lies inside vertical line p1-p2
            (x1 == x2 == px and y1 < py < y2)
        ):
            # XXX
            # - return normalized line or this line created in clockwise order?
            return (p1, p2)

def _corners_pairs(pairs, point_on_rect):
    prx, pry = point_on_rect
    is_last = False
    for p1, p2 in pairs:
        yield p1
        x1, y1 = p1
        x2, y2 = p2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        if y1 == y2 == pry and x1 <= prx <= x2:
            yield point_on_rect
            break
        elif x1 == x2 == prx and y1 <= pry <= y2:
            yield point_on_rect
            break
    else:
        is_last = True
    # avoid unnecessary checks for point_on_rect
    for p1, p2 in pairs:
        yield p1
    yield p2
    if is_last:
        yield point_on_rect

def corners_with_point(rect, point_on_rect):
    pairs = it.pairwise(corners(rect))
    return _corners_pairs(pairs, point_on_rect)

def ccw_corners_with_point(rect, point_on_rect):
    pairs = it.pairwise(ccw_corners(rect))
    return _corners_pairs(pairs, point_on_rect)

def ccw_side_lines_from_point(rect, point):
    ccw_sides = list(ccw_side_lines(rect))
    for i in range(4):
        if point_on_line_segment(ccw_sides[i], point):
            break
    for i in range(i, i+4):
        yield ccw_sides[i % 4]

def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def get_digits(s):
    # TODO: move this func
    for char in s:
        if char in string.digits:
            yield char

def best_name_colors(color_items):
    # NOTES
    # - pygame.color.THECOLORS has many names for some colors
    # - for instance 'grey100', 'gray100', and 'white' are all white.
    # - also 'red' and 'red1' are the same.
    # Here, we group color items by the tuple value and yield the highest
    # quality name. We prefer least amount of digits in name.
    second = op.itemgetter(1)
    grouped = sorted_groupby(color_items, key=second)

    def _quality(color_item):
        # count of digits in key
        key, val = color_item
        return len(list(get_digits(key)))

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

def get_rects_flow(images, flowx=0, flowy=0):
    """
    :param images: indexable of images
    :param flowx: boolean or scale amount of influence
    As in, flowx=True mean "flow in the x direction"
    """
    images = iter(images)
    rect = next(images).get_rect()
    yield rect
    x, y = rect.bottomright
    for image in images:
        rect = image.get_rect(x=flowx*x, y=flowy*y)
        yield rect
        x, y = rect.bottomright

def flow(rects, flowx=0, flowy=0):
    # NOTE
    # - must be pygame.Rect or similar to modify
    if not flowx and not flowy:
        raise ValueError('one flow arg required')
    rects = iter(rects)
    x, y = next(rects).bottomright
    for rect in rects:
        rect.x += flowx * x
        rect.y += flowy * y
        # XXX
        # - this probably makes it impossible to flow other than right and
        #   down.
        x, y = rect.bottomright

def make_blitables_from_font(lines, font, color, antialias=True):
    images = tuple(font.render(line, antialias, color) for line in lines)
    rects = tuple(image.get_rect() for image in images)
    flow_topbottom(rects)
    return (images, rects)

def move_as_one(rects, **kwargs):
    orig = pygame.Rect(wrap(rects))
    dest = pygame.Rect(make_rect(orig, **kwargs))
    delta = pygame.Vector2(dest.topleft) - orig.topleft
    for rect in rects:
        rect.topleft += delta
    return delta

def clamp_as_one(target, rects, inside):
    """
    Move `rects` as one such that `target` is contained by `inside`.
    """
    orig = pygame.Rect(wrap(rects))
    target_dest = pygame.Rect(target).clamp(inside)
    delta = pygame.Vector2(target_dest.topleft) - pygame.Rect(target).topleft
    for rect in rects:
        rect.topleft += delta

# TODO
# - would like default font attributes
# - how to customize though?
# - how to access?
# - eventually want markup/undertale styling of words and letters and whatnot
# - have to have a font for every styling
#   like bold, requires a new font object

default_font_style = dict(
    bold = False,
    italic = False,
)

def system_font(name, size, **style):
    # init is very cheap and this removes a pain point
    # timeit: 10000000 loops, best of 5: 24.1 nsec per loop
    pygame.font.init()
    for key, val in default_font_style.items():
        style.setdefault(key, val)
    return pygame.font.SysFont(name, size, **style)

def sans_serif_font(size, **style):
    return system_font('sans-serif', size, **style)

def monospace_font(size, **style):
    return system_font('monospace', size, **style)

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

def render_rect(surf, color, rect, *draw_args, **draw_kwargs):
    # render rect onto image for alpha
    image = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(image, color, ((0,0), rect.size), *draw_args, **draw_kwargs)
    return surf.blit(image, rect)

def blit(surface, source, dest, area=None, special_flags=0):
    # standalone callable for some_surface.blit(source, dest, ...)
    return surface.blit(source, dest, area, special_flags)

def blit_rect(surf, rect, color):
    x, y, w, h = rect
    image = pygame.Surface((w, h), pygame.SRCALPHA)
    image.fill(color)
    return surf.blit(image, image.get_rect(topleft=(x, y)))

def circle_rect(center, radius):
    """
    Return a rect that wraps a circle.
    """
    x, y = center
    return (x-radius, y-radius, radius*2, radius*2)

def circle_inside(rect):
    """
    Return required args for drawing a circle inside a rect.
    """
    x, y, w, h = rect
    radius = min(w, h) // 2
    center = (x + radius, y + radius)
    return (center, radius)

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

def line_rect_intersections(line1, rect):
    # line to line-of-rect intersections
    if is_hline(line1):
        func = vlines
    else:
        func = hlines
    for line2 in func(rect):
        intersection = line_line_intersection(line1, line2)
        if intersection:
            yield (intersection, line2)

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

def nearest_point_on_segment(point, segment_start, segment_end):
    # TODO
    # - clean this up from chatgpt

    # Calculate the direction vector of the line segment
    segment_vector = (segment_end[0] - segment_start[0], segment_end[1] - segment_start[1])

    # Vector from segment start to the given point
    point_vector = (point[0] - segment_start[0], point[1] - segment_start[1])

    # Calculate dot product
    dot_product = point_vector[0] * segment_vector[0] + point_vector[1] * segment_vector[1]
    segment_length_squared = segment_vector[0] * segment_vector[0] + segment_vector[1] * segment_vector[1]

    # Calculate projection parameter
    if segment_length_squared == 0:
        projection = 0
    else:
        projection = dot_product / segment_length_squared

    # If projection is less than 0, closest point is the segment start
    if projection <= 0:
        return segment_start

    # If projection is greater than 1, closest point is the segment end
    if projection >= 1:
        return segment_end

    # Closest point lies within the segment
    closest_point = (segment_start[0] + projection * segment_vector[0], segment_start[1] + projection * segment_vector[1])
    return closest_point

def nearest_point_on_rect(point, rect):
    points = (
        nearest_point_on_segment(point, p1, p2)
        for p1, p2 in side_lines(rect)
    )
    return min(points, key=lambda p: math.dist(point, p))

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

#def line_line_intersection2(x1, y1, x2, y2, x3, y3, x4, y4):
def line_line_intersection2(line1, line2):
    # works!
    return find_intersection(line1[0], line1[1], line2[0], line2[1])
    return find_intersection((x1, y1), (x2, y2), (x3, y3), (x4, y4))

def line_line_intersection(line1, line2):
    line1p1, line1p2 = line1
    line2p1, line2p2 = line2
    return find_intersection(line1p1, line1p2, line2p1, line2p2)

def rect_rect_intersections(rect1, rect2):
    # TODO
    # - demo for this function
    for func1, func2 in [(hlines, vlines), (vlines, hlines)]:
        for line1, line2 in it.product(func1(rect1), func2(rect2)):
            intersect = line_line_intersection(line1, line2)
            if intersect:
                yield intersect

def is_hline(line):
    # y's are equal
    return line[0][1] == line[1][1]

def is_vline(line):
    # x's are equal
    return line[0][0] == line[1][0]

def resolve_rect_collisions(rects, iterations):
    # - mutates the rect objects
    # TODO
    # - resolve needs work
    for n in it.count():
        if n > iterations:
            break
        overlaps = tuple(_overlaps(rects))
        if not overlaps:
            break
        for r1, r2, overlap in overlaps:
            if not overlap:
                continue
            if r1 == r2:
                r1.left -= r2.width / 2
                r2.right += r1.width / 2
            else:
                dx, dy = pygame.Vector2(r2.center) - r1.center
                if abs(dx) > abs(dy):
                    if dx > 0:
                        r1.left = r2.right
                    else:
                        r1.right = r2.left
                else:
                    if dy > 0:
                        r1.bottom = r2.top
                    else:
                        r1.top = r2.bottom

def outline_by_path(rect1, rect2):
    for hline in hlines(rect1):
        intersections = list(line_rect_intersections(hline, rect2))
        if not intersections:
            yield hline
        else:
            yield (hline[0], intersections[0][0])
            yield (hline[1], intersections[-1][0])

def reflow_from(list_, item):
    """
    Loop through list_, find item, and then from there yield it, yield the
    remaining, and finally the item before it in list_ order.
    """
    list_iter = iter(list_)
    stack = []
    for thing in list_iter:
        if thing == item:
            yield thing
            break
        else:
            stack.append(thing)
    for thing in list_iter:
        yield thing
    for thing in stack:
        yield thing

def _outline_rects_ccw(intersection_point, rect1, rect2):
    # support function for outline_rects
    rect_line = find_line_for_point(rect1, intersection_point)
    ccw_lines = tuple(ccw_side_lines(rect1))
    if rect_line not in ccw_lines:
        return
    for p1, p2 in reflow_from(ccw_lines, rect_line):
        _intersection_points = list(line_rect_intersections((p1, p2), rect2))
        if _intersection_points:
            yield _intersection_points[0]
            break
        yield p2

def outline_rects(rect1, rect2):
    rect1 = pygame.Rect(rect1)
    rect2 = pygame.Rect(rect2)
    # loop rect1 points clockwise
    points = tuple(corners(rect1))
    for index, p1 in enumerate(points):
        p2 = points[(index + 1) % 4]
        line1 = (p1, p2)
        # 1. no intersections
        # 2. one intersection
        # 3. two intersections
        intersection_line_pairs = tuple(line_rect_intersections(line1, rect2))
        if not intersection_line_pairs:
            yield p1
        else:
            ipoints, ilines = zip(*intersection_line_pairs)
            n = len(ipoints)
            if n == 1:
                if rect2.collidepoint(p1):
                    yield ipoints[0]
                    yield p2
                    # TODO
                    # - same as below, in else block for this point
                else:
                    # p1-p2 line is going into rect2
                    yield p1
                    yield ipoints[0]
                    # now loop the points on rect2 from intersection, ccw,
                    # until intersection with rect1

                    # 1. find the points on rect2 that intersection lies on
                    # 2. loop from intersection point to other points on rect2,
                    #    counterclockwise
                    # 3. when a pair of points on rect2 intersects rect1 again,
                    #    yield inner point, intersection point then break
                    # 4. resume here, from intersection point

                    yield from _outline_rects_ccw(ipoints[0], rect2, rect1)

            elif n == 2:
                # XXX
                continue
                # line p1-p2 goes all the way through rect2
                nearest = min(ipoints, key=lambda p: math.dist(p1, p))
                yield p1
                yield nearest
            else:
                raise NotImplementedError

def rect_rect_segments(rect1, rect2):
    for func1, func2 in ((hlines, vlines), (vlines, hlines)):
        for line1, line2 in it.product(func1(rect1), func2(rect2)):
            intersect = line_line_intersection2(line1, line2)
            if intersect:
                # yield intersection point and other point outside first rect
                outside_point = next(
                    point for point in line2
                    if not rect1.collidepoint(point)
                )
                yield (outside_point, intersect)
            elif not any(p for p in line2 if rect1.collidepoint(p)):
                yield line2

def point_inside(rect, point):
    """
    Test if point is inside rect. Fixes inconsistency of
    pygame.rect.collidepoint that returns true for top and left sides.
    """
    x, y = point
    return rect.left < x < rect.right and rect.top < y < rect.bottom

def rect_rect_segments(rect1, rect2):
    overlap = rect1.clip(rect2)
    for rect in [rect1, overlap]:
        for point in corners(rect):
            if not point_inside(rect2, point):
                yield point

def walk_outline(rect1, rect2):
    lines1 = side_lines(rect1)
    for line1 in lines1:
        intersections = tuple(line_rect_intersections(line1, rect2))
        if not any(intersections):
            yield line1
            continue

        line1_p1, line1_p2 = line1
        if not point_inside(rect2, line1_p1):
            outside = line1_p1
        else:
            outside = line1_p2

        nearest_intersection = min(intersections, key=lambda ip: math.dist(ip, outside))
        partial_line1 = (outside, nearest_intersection)
        yield partial_line1

        # walk other rect from intersection point

        # find the side-line the intersection was on
        for line2 in ccw_side_lines_from_point(rect2, nearest_intersection):
            intersections = tuple(line_rect_intersections(line2, rect1))
            if not any(intersections):
                if not any(point_inside(rect1, point) for point in line2):
                    # line outside
                    break
                yield line2
                continue

            # line intersection
            line2_p1, line2_p2 = line2
            # point inside other rect, rect1
            if point_inside(rect1, line2_p1):
                inside = line2_p1
            else:
                inside = line2_p2

            nearest_intersection = min(intersections, key=lambda ip: math.dist(ip, inside))
            yield (inside, nearest_intersection)

        break

    for line1 in lines1:
        if point_on_line_segment(line1, nearest_intersection):
            p1, p2 = line1
            if not point_inside(rect2, p1):
                p = p1
            else:
                p = p2
            yield (nearest_intersection, p)
        else:
            yield line1

def walk_outline_pointwise(rect1, rect2):
    for p1, p2 in it.pairwise(corners(rect1)):
        line1 = (p1, p2)
        intersections = tuple(line_rect_intersections(line1, rect2))
        if intersections:
            yield p1
            ipoint = min(intersections, key=lambda p: math.dist(p1, p))
            yield ipoint

            break
            for _line in ccw_side_lines_from_point(rect2, ipoint):
                _p1, _p2 = _line
                if not (rect1.collidepoint(_p1) or rect1.collidepoint(_p2)):
                    continue
                if point_on_line_segment(_line, ipoint):
                    yield ipoint
                    if rect1.collidepoint(_p1):
                        yield _p1
                    else:
                        yield _p2
                else:
                    _intersections = tuple(line_rect_intersections(_line, rect1))
                    if _intersections:
                        if rect1.collidepoint(_p1):
                            _p = _p1
                        else:
                            _p = _p2
                        yield _p
                        _ipoint = min(intersections, key=lambda p: math.dist(_p, p))
                        yield _ipoint
                    else:
                        yield _p1
                        yield _p2

            # sort rect2 point ccw
            # find ipoint between pairs
            # starting there yield pairs until another intersection
            # yield nearest intersection point line
            # resume yield rect1 points

            break
        yield p1
        yield p2

def walk_outline_pointwise(rect1, rect2):
    for p1, p2 in it.pairwise(corners(rect1)):
        line1 = (p1, p2)
        intersections = tuple(line_rect_intersections(line1, rect2))
        if intersections:
            yield p1
            nearest = min(intersections, key=lambda p: math.dist(p1, p))
            yield nearest
            for _line in ccw_side_lines_from_point(rect2, nearest):
                _p1, _p2 = _line
                if rect2.collidepoint(_p1):
                    yield _p1
            break
        else:
            yield p1

def atan2_points(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.atan2(y2 - y1, x2 - x1)

def point_on_line_segment(line, point):
    (x1, y1), (x2, y2) = line
    x, y = point
    if (y - y1) * (x2 - x1) == (y2 - y1) * (x - x1):
        if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            return True

def is_axis_aligned(line):
    p1, p2 = line
    return p1[0] == p2[0] or p1[1] == p2[1]

def slope(line):
    (x1, y1), (x2, y2) = line
    dx = (x2 - x1)
    if dx == 0:
        return
    return (y2 - y1) / dx

def line_midpoint(line):
    p1, p2 = line
    x1, y1 = p1
    x2, y2 = p2

    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    return (x1 + ((x2 - x1) / 2), y1 + ((y2 - y1) / 2))

    p1 = pygame.Vector2(p1)
    p2 = pygame.Vector2(p2)
    return p1 + (p2 - p1) / 2

def flatten_line(line):
    p1, p2 = line
    return (*p1, *p2)

def flatten_lines(*lines):
    return tuple(flatten_line(line) for line in lines)

def rect_from_size(*args, x=0, y=0):
    if len(args) == 1:
        w, h = args[0]
    elif len(args) == 2:
        w, h = args
    else:
        raise ValueError('one or two positional arguments required')
    return (x, y, w, h)

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

def random_rect2(inside, minsize=None, maxsize=None):
    left, top, width, height = inside

    if minsize is None:
        minsize = (1, 1)
    minwidth, minheight = minsize

    if maxsize is None:
        maxsize = (width - minwidth, height - minheight)
    maxwidth, maxheight = maxsize

    _width = random.randint(minwidth, maxwidth)
    _height = random.randint(minheight, maxheight)

    right = (left + width) - _width
    bottom = (top + height) - _height

    x = random.randint(left, right)
    y = random.randint(top, bottom)

    return (x, y, _width, _height)

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

def wrap(rects):
    # duplicate to fix
    xs, ys, widths, heights = zip(*map(tuple, rects))
    rights = (x + w for x, w in zip(xs, widths))
    bottoms = (y + h for y, h in zip(ys, heights))
    x = min(xs)
    y = min(ys)
    right = max(rights)
    bottom = max(bottoms)
    return (x, y, right - x, bottom - y)

def extremities(*rects):
    """
    Clockwise scalar sides of rect(s) starting from top.
    """
    xs, ys, ws, hs = zip(*map(tuple, rects))
    left = min(xs)
    top = min(ys)
    width = max(ws)
    height = min(hs)
    right = left + width
    bottom = top + height
    return (top, right, bottom, left)

def size_from_points(points):
    xs, ys = zip(*points)
    x = min(xs)
    y = min(ys)
    r = max(xs)
    b = max(ys)
    w = r - x
    h = b - y
    return (w, h)

def rect_from_points(points):
    xs, ys = zip(*points)
    x = min(xs)
    y = min(ys)
    r = max(xs)
    b = max(ys)
    w = r - x
    h = b - y
    return (x, y, w, h)

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

def corner_angle(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    AB = (x2 - x1, y2 - y1)
    BC = (x3 - x2, y3 - y2)
    dot_product = AB[0] * BC[0] + AB[1] * BC[1]
    magnitude_AB = math.sqrt(AB[0]**2 + AB[1]**2)
    magnitude_BC = math.sqrt(BC[0]**2 + BC[1]**2)
    cos_theta = dot_product / (magnitude_AB * magnitude_BC)
    angle = math.acos(cos_theta)
    return angle

def corner_angle(p1, p2, p3):
    # https://stackoverflow.com/a/31334882/2680592
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    return math.atan2(y3 - y1, x3 - x1) - math.atan2(y2 - y1, x2 - x1)

def arc_length(radius, a, b):
    return radius * abs(b - a)

def arc_length_longest(radius, a, b):
    longest_distance = math.tau - abs(a - b)
    return radius * longest_distance

def circle_point(angle, radius):
    """
    Screen-space point on a circle.
    """
    return (math.cos(angle) * radius, math.sin(angle) * radius)

def circle_points(degrees, radius):
    """
    :param degrees: iterable of integer angles in degrees.
    """
    for angle in map(math.radians, degrees):
        x = +math.cos(angle) * radius
        y = -math.sin(angle) * radius
        yield (x, y)

def outer_tangent_angles(center, radius, point):
    """
    Generate the two angles from the center to the tangent points formed by a
    circle and an external point.
    """
    d = math.dist(center, point)
    if d < radius:
        return
    cx, cy = center
    px, py = point
    angle = angle_to(center, point)
    alpha = math.asin(radius / d)
    beta = math.tau / 4 - alpha
    yield angle - beta
    yield angle + beta

def atan2_full(dy, dx):
    return math.atan2(dy, dx) % math.tau

def absolute_angle(p1, p2):
    # NOTE
    # - return for screen space
    p1x, p1y = p1
    p2x, p2y = p2
    return atan2_full(-(p2y - p1y), p2x - p1x)

def lines_arc(center, radius, p1, p2, divisor):
    """
    Generate points for an arc on a circle from p1 to p2.
    """
    start_angle = int(math.degrees(absolute_angle(center, p1)))
    end_angle = int(math.degrees(absolute_angle(center, p2)))
    between_degrees = end_angle - start_angle
    step = abs(between_degrees // divisor)
    if start_angle > end_angle:
        step = -step
    degrees = range_with_end(start_angle, end_angle, step)
    cx, cy = center
    for px, py in circle_points(degrees, radius):
        yield (cx + px, cy + py)

def circle_slope_tangent(center, point):
    cx, cy = center
    x, y = point
    derivative_x = 2 * (x - cx)
    derivative_y = 2 * (y - cy)
    slope = derivative_x / derivative_y
    return slope

def circle_collision(circle1, circle2):
    center1, r1 = circle1
    center2, r2 = circle2
    d = math.dist(center1, center2)
    return d < r2 + r1

def rect_collision(r1, r2):
    return pygame.Rect(r1).colliderect(r2)

def rect_clip(r1, r2):
    return pygame.Rect(r1).clip(r2)

def point_on_axisline(point, line):
    px, py = point
    (x1, y1), (x2, y2) = line
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    return (
        (py == y1 == y2 and x1 <= px <= x2)
        or
        (px == x1 == x2 and y1 <= py <= y2)
    )

def point_inside_line(point, line):
    px, py = point
    (x1, y1), (x2, y2) = line
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    return (
        py == y1 == y2 and x1 < px < x2
        or
        px == x1 == x2 and y1 < py < y2
    )

def axis_line_inside_another(line, other):
    for point in line:
        if point_inside_line(point, other):
            return True

def bisect_axis_line(line, point):
    # caller should verify point on line
    if point in line:
        yield line
    else:
        # point is not one of the endpoints of the line
        x, y = point
        p1, p2 = line
        x1, y1 = p1
        x2, y2 = p2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        if x1 == x2:
            # line is vertical
            # yield top section
            yield ((x, y1), (x, y))
            # yield bottom section
            yield ((x, y), (x, y2))
        elif y1 == y2:
            # line is horizontal
            # yield left section
            yield ((x1, y), (x, y))
            yield ((x, y), (x2, y))

def graph_from_circle(center, radius, step, start_angle=0, end_angle=360):
    """
    Return a dict of points and their neighbors.
    """
    cx, cy = center
    degrees = range(start_angle, end_angle, step)
    points_on_circle = [
        (cx + px, cy + py) for px, py in circle_points(degrees, radius)
    ]
    n = len(points_on_circle)
    graph = defaultdict(list)
    graph[center] = points_on_circle
    for index, point in enumerate(points_on_circle):
        graph[point].append(center)
        for delta in [-1, +1]:
            neighbor_index = (index + delta) % n
            graph[point].append(points_on_circle[neighbor_index])
    return graph

def random_path_circle(
    all_points,
    circle_points,
    center,
    start,
    end,
):
    # TODO
    # - build a real graph to randomly find paths through
    n = len(circle_points)
    path = [start]
    while path[-1] != end:
        # center is always a neighbor
        neighbors = [center]
        if path[-1] in circle_points:
            # last point is on the circle
            index = circle_points.index(path[-1])
            # add points on circle either side of last point
            neighbors += [
                circle_points[(index - 1) % n],
                circle_points[(index + 1) % n],
            ]
        else:
            # last point is center, so any point on circle is neighbor
            neighbors += circle_points
        point = random.choice(neighbors)
        if point not in path:
            path.append(point)
    return path


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


class matchall:
    """
    Callable returning true if all regular expressions match.
    """

    def __init__(self, *regular_expressions):
        self.regular_expressions = list(map(re.compile, regular_expressions))

    def __call__(self, *values):
        items = zip(self.regular_expressions, values)
        return all(re_.match(value) for re_, value in items)


class typed_container:
    """
    Callable to take an iterable and type its items; and place them in a
    container.
    """

    def __init__(self, container, type_):
        self.container = container
        self.type_ = type_

    def __call__(self, iterable):
        return self.container(map(self.type_, iterable))


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

# graphs and traversal

def make_graph(nodes, is_edge):
    graph = defaultdict(list)
    # make all the nodes appear in the graph
    for node in nodes:
        graph[node]
    for node1, node2 in it.combinations(nodes, 2):
        if is_edge(node1, node2):
            graph[node1].append(node2)
            graph[node2].append(node1)
    return graph

def depth_first_search(graph, start):
    visited = set()
    stack = [start]
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        yield current
        visited.add(current)
        for neighbor in reversed(graph[current]):
            if neighbor in visited:
                continue
            stack.append(neighbor)

def unique_paths(graph):
    """
    Generate unique paths between all nodes, disregarding order.
    """
    # graph: { node: iterable(connected_nodes), ... }
    # need mutable that can contain sets
    _paths = []
    for node in graph:
        path = tuple(depth_first_search(graph, node))
        if set(path) not in _paths:
            yield path
            _paths.append(set(path))

def _overlaps(rects):
    for r1, r2 in it.product(rects, repeat=2):
        yield (r1, r2, r1.clip(r2))

def contains_point(rect, point):
    # point collides without being one of our corners
    x, y, w, h = rect
    r = x + w
    b = y + h
    # TODO
    # - check also not on side/edge line?
    if point not in ((x,y), (r,y), (r,b), (x,b)):
        return pygame.Rect(rect).collidepoint(point)

def deltas_for_size(side_size):

    half_side_size = side_size // 2

    def _delta(index):
        values = divmod(index, side_size)
        return tuple(v - half_side_size for v in values)

    deltas = set(map(_delta, range(side_size*side_size)))
    return deltas

# clockwise ordered rect side attribute names mapped with their opposites
SIDENAMES = ['top', 'right', 'bottom', 'left']
SIDES = dict(opposite_items(SIDENAMES))

# clockwise ordered rect point attribute names mapped with their opposites
POINTS = dict(opposite_items(tuple(point_attrs(tuple(SIDES)))))

EMPTY_RECT = (0, 0, 0, 0)

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

UNIQUE_COLORSTHE_COLORFUL = {k: v for k, v in UNIQUE_COLORSTHE.items() if len(set(k)) > 2}

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

DELTAS = set(tuple(v - 1 for v in divmod(i, 3)) for i in range(9))
DELTAS.remove((0,0))
