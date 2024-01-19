import argparse
import code
import contextlib
import functools
import io
import itertools as it
import math
import operator as op
import sys
import textwrap
import unittest

import pygamelib

from pygamelib import pygame

try:
    sys.ps1
except AttributeError:
    sys.ps1 = '>>> '

try:
    sys.ps2
except AttributeError:
    sys.ps2 = '... '

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


class InteractiveConsole(code.InteractiveConsole):
    """
    InteractiveConsole that saves output into a list.
    """

    def __init__(self, locals=None):
        super().__init__(locals=locals)
        self.stdout = []

    def runcode(self, code):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            super().runcode(code)
            self._stdout(stdout.getvalue())

    def write(self, data):
        self._stdout(data)

    def _stdout(self, text):
        self.stdout.extend(text.splitlines())


class Ticker:

    def __init__(self, length, start=0):
        self.length = length
        self.index = start

    def update(self, advance=1):
        self.index = (self.index + advance) % self.length


class Editor(pygamelib.DemoBase):

    def __init__(self, shapes=None):
        if shapes is None:
            shapes = []
        self.shapes = shapes
        self.font = pygame.font.SysFont('monospace', 18)
        self.text_color = 'white'
        self.caret_image = pygame.Surface(self.font.size(' '))
        self.caret_image.fill(self.text_color)
        self.caret_blink = Ticker(60)
        self.interactive = InteractiveConsole(
            locals = dict(
                editor = self,
                shapes = self.shapes,
                circle = self.create_circle,
            ),
        )
        self.readline = pygamelib.Readline(self._read_input)
        self.text_wrapper = textwrap.TextWrapper()

    def create_circle(self, color, position, radius):
        try:
            pygame.Color(color)
        except ValueError:
            self.interactive.showtraceback()
            return
        self.shapes.append(('circle', color, position, radius))

    def _read_input(self, line):
        # save input line with prompt to "stdout"
        self.interactive.write(self.readline.full_input_line())
        # evaluate line
        self.readline.more = self.interactive.push(line)

    def start(self, engine):
        super().start(engine)
        self.console_rect = self.window.copy()
        scale = 4
        size = tuple(map(lambda value: value / scale, self.window.size))
        self.buffer = pygame.Surface(size)

    def update(self):
        super().update()
        self.caret_blink.update()
        self.draw()

    def do_quit(self, event):
        self.engine.stop()

    def __do_keydown(self, event):
        pygamelib.dispatch(self.readline, event)
        pygamelib.post_videoexpose()

    def draw_shapes(self, surf):
        for shape, color, *args in self.shapes:
            func = getattr(pygame.draw, shape, None)
            func(surf, color, *args)

    def _console_lines(self):
        for line in self.interactive.stdout:
            for wrapped_line in self.text_wrapper.wrap(line):
                yield wrapped_line

    def _lines_for_draw(self):
        lines = list(self._console_lines()) + [self.readline.full_input_line()]
        return lines

    def draw_interactive(self):
        lines = self._lines_for_draw()
        images, rects = pygamelib.make_blitables_from_font(lines, self.font, self.text_color)
        lines_rect = pygame.Rect(pygamelib.wrap(rects))
        if not self.console_rect.contains(lines_rect):
            pygamelib.move_as_one(rects, bottomleft=self.console_rect.bottomleft)
        pygame.draw.rect(self.screen, self.text_color, lines_rect, 1)
        for image, rect in zip(images, rects):
            if self.console_rect.colliderect(rect):
                self.screen.blit(image, rect)

        # blinking caret
        if self.caret_blink.index < self.framerate / 2:
            input_line = self.readline.input_lines[self.readline.input_index]
            before_text, after_text = input_line.split()
            offsetx, offsety = self.font.size(self.readline.prompt() + before_text)
            caret_rect = self.caret_image.get_rect(
                left = rects[-1].left + offsetx,
                bottom = rects[-1].bottom,
            )
            self.screen.blit(self.caret_image, caret_rect)

    def draw(self):
        self.screen.fill('black')
        self.draw_shapes(self.screen)
        #self.draw_interactive()
        #pygame.transform.scale(self.buffer, self.window.size, self.screen)
        pygame.display.flip()

    def do_videoexpose(self, event):
        self.draw()


class ShapeBrowser(pygamelib.BrowseBase):

    def __init__(self, font, scale, shapes):
        self.font = font
        self.scale = scale
        self._shapes = shapes
        self.update_shapes_scale()

    def update_shapes_scale(self):
        self.shapes = [scale_shape(shape, self.scale) for shape in self._shapes]

    def do_videoexpose(self, event):
        self.draw()

    def do_mousewheel(self, event):
        if 0 < self.scale + event.y < 100:
            self.scale += event.y
            self.update_shapes_scale()
            pygamelib.post_videoexpose()

    def draw(self):
        self.screen.fill('black')
        ox, oy = self.offset
        for name, color, *rest in self.shapes:
            func = getattr(pygame.draw, name)
            if name == 'circle':
                (x, y), radius, width = rest
                x -= ox
                y -= oy
                rest = ((x, y), radius, width)
            elif name == 'rect':
                (x, y, w, h), width, *borderargs = rest
                rest = ((x-ox, y-oy, w, h), width, *borderargs)
            elif name == 'line':
                (x1, y1), (x2, y2), width = rest
                rest = ((x1-ox, y1-oy), (x2-ox, y2-oy), width)
            func(self.screen, color, *rest)
        text = self.font.render(f'{self.scale}', True, 'white')
        self.screen.blit(text, (0,)*2)
        pygame.display.flip()


def run(screen_size, shapes, scale):
    pygame.font.init()
    font = pygame.font.SysFont('monospace', 20)
    editor = ShapeBrowser(font, scale, shapes)
    engine = pygamelib.Engine()
    pygame.display.set_mode(screen_size)
    engine.run(editor)

shapenames = set(n for n in dir(pygame.draw) if not n.startswith('_'))
shapenames.add('squircle')
colornames = set(pygame.color.THECOLORS)

def rectquadrants(rect):
    half_size = (rect.width / 2, rect.height / 2)
    yield ((rect.x, rect.y), half_size)
    yield ((rect.centerx, rect.y), half_size)
    yield ((rect.centerx, rect.centery), half_size)
    yield ((rect.x, rect.centery), half_size)

def mergeable(range1, range2):
    start1, stop1 = range1
    start2, stop2 = range2
    return not (start1 > stop2 or stop1 < start2)

def merge_ranges(ranges):
    ranges = set(ranges)
    if not ranges:
        return ranges
    while ranges:
        combos = it.combinations(ranges,2)
        mergeables = set((r1, r2) for r1, r2 in combos if mergeable(r1, r2))
        if not mergeables:
            return ranges
        for r1, r2 in mergeables:
            if r1 in ranges:
                ranges.remove(r1)
            if r2 in ranges:
                ranges.remove(r2)
            ranges.add((min(*r1, *r2), max(*r1, *r2)))

def squircle_shapes(color, center, radius, width, corners):
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
        anglepairs = merge_ranges(anglepairs)
        for anglepair in anglepairs:
            angle1, angle2 = map(math.radians, anglepair)
            yield ('arc', color, rect, angle1, angle2, width)
        for line in lines:
            yield ('line', color, *line, width)

def parse(file):
    context = dict()
    for line in file:
        line = line.lstrip()
        if not line or line.startswith('#'):
            continue
        shape = line.split()
        name, color, *remaining = shape
        assert name in shapenames
        assert color in colornames
        if name == 'arc':
            x, y, w, h, angle1, angle2, width = map(eval, remaining)
            # avoid argument that results in nothing being drawn
            assert width != 0
            angle1, angle2 = map(math.radians, [angle1, angle2])
            yield (name, color, (x, y, w, h), angle1, angle2, width)
        elif name == 'circle':
            x, y, radius, width = map(eval, remaining)
            yield (name, color, (x, y), radius, width)
        elif name == 'line':
            x1, y1, x2, y2, width = map(eval, remaining)
            # avoid nothing drawn
            assert width > 0
            yield (name, color, (x1, y1), (x2, y2), width)
        elif name == 'lines':
            closed, width, *remaining = map(eval, remaining)
            closed = bool(closed)
            width = eval(width)
            # avoid nothing drawn
            assert width > 0
            points = tuple(it.pairwise(map(eval, remaining)))
            yield (name, color, closed, points, width)
        elif name == 'rect':
            x, y, w, h, width, *borderargs = map(eval, remaining)
            yield (name, color, (x, y, w, h), width, *borderargs)
        elif name == 'squircle':
            x, y, radius, width, *corners = remaining
            x, y, radius, width = map(eval, (x, y, radius, width))
            assert all(corner in pygamelib.CORNERNAMES for corner in corners), corners
            yield from squircle_shapes(color, (x, y), radius, width, corners)

def scale_shape(shape, scale):
    def _scale(value):
        return value * scale

    name, color, *rest = shape
    if name == 'circle':
        center, radius, width = rest
        center = tuple(map(_scale, center))
        return (name, color, center, radius*scale, width*scale)
    elif name == 'rect':
        rect, width, *borderargs = rest
        rect = tuple(map(_scale, rect))
        borderargs = map(_scale, borderargs)
        return (name, color, rect, width*scale, *borderargs)
    elif name == 'line':
        start, end, width = rest
        start = tuple(map(_scale, start))
        end = tuple(map(_scale, end))
        return (name, color, start, end, width*scale)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'shapes',
        type = argparse.FileType(),
    )
    parser.add_argument(
        '--scale',
        type = int,
        default = 1,
        help = 'Scale shapes',
    )
    parser.add_argument(
        '--screen-size',
        type = pygamelib.sizetype(),
        default = '800',
    )
    args = parser.parse_args(argv)

    if args.shapes:
        shapes = list(parse(args.shapes))
    else:
        shapes = None

    run(args.screen_size, shapes, args.scale)

if __name__ == '__main__':
    main()
