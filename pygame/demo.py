import argparse
import itertools as it
import math
import random

from xml.etree import ElementTree

import pygamelib

from pygamelib import pygame

class Stat:

    def __init__(self):
        self.minval = +math.inf
        self.maxval = -math.inf

    def update(self, value):
        if value < self.minval:
            self.minval = value
        if value > self.maxval:
            self.maxval = value


class KeydownVariables:

    def __init__(self, variables):
        self.variables = variables

    def find_match_for_letter(self, letter):
        # either the exact letter or only one match for startswith
        match = None
        varkeys = [varkey for varkey in self.variables if varkey.startswith(letter)]
        if letter in self.variables:
            return letter
        elif len(varkeys) == 1:
            return varkeys[0]

    def handle_keydown(self, event):
        match = self.find_match_for_letter(event.unicode.lower())
        if match:
            if event.mod & pygame.KMOD_SHIFT:
                self.variables.decrease(match)
            else:
                self.variables.increase(match)
            return True


class VariableManager:

    def __init__(self, variables, deltas=None):
        self.variables = variables
        if deltas is None:
            deltas = {}
        self.deltas = deltas

    def __getitem__(self, name):
        return self.variables[name]

    def __iter__(self):
        return iter(self.variables)

    def increase(self, name):
        delta = self.deltas.get(name, 1)
        self.variables[name] += delta

    def decrease(self, name):
        delta = self.deltas.get(name, 1)
        self.variables[name] -= delta


class GradientLineRenderer:

    def __init__(self, steps, length):
        """
        :param steps: number of segments along line.
        :param length: length of each side of perpendicular lines.
        """
        self.steps = steps
        self.length = length

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(steps=kwargs['steps'], length=kwargs['length'])

    def update_from_dict(self, **kwargs):
        self.steps = kwargs['steps']
        self.length = kwargs['length']

    # NOTES
    # - a function like enumerate that associates a time with an iterable over
    #   a number of steps?

    def points_times(self, line):
        lines = pygamelib.perpendicular_line_segments(line, self.steps, self.length)
        for i, points in enumerate(pygamelib.line_segments_polygons(lines)):
            time = i / (self.steps - 1)
            yield (points, time)

    def draw(self, surface, line, color1, color2, border_color=None, border_width=None):
        for points, time in self.points_times(line):
            color = pygame.Color(color1).lerp(color2, time)
            pygame.draw.polygon(surface, color, points)
            if border_color:
                assert border_width is not None
                pygame.draw.polygon(surface, border_color, points, border_width)


class BlitTilesDemo(
    pygamelib.DemoBase,
    pygamelib.QuitKeydownMixin,
    pygamelib.StopMixin,
):

    def __init__(self, display_size, tilesize, font):
        self.display_size = display_size
        self.tilesize = tilesize
        self.font = font
        self.fps_stats = Stat()
        self.update_blits()

    def update_blits(self):
        self.tile = pygame.Surface(self.tilesize)
        pygame.draw.circle(
            self.tile,
            'red',
            self.tile.get_rect().center,
            min(self.tilesize)/4
        )
        window_width, window_height = self.display_size
        tile_width, tile_height = self.tilesize

        self.blits = list(zip(
            it.repeat(self.tile),
            it.product(
                range(0, window_width, tile_width),
                range(0, window_height, tile_height)
            )
        ))

    def update(self):
        self.clock.tick()
        for event in pygame.event.get():
            pygamelib.dispatch(self, event)
        pygamelib.post_videoexpose()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        self.screen.blits(self.blits)
        fps = self.clock.get_fps()
        self.fps_stats.update(fps)
        lines = (
            f'fps={fps:04.0f}',
            f'minfps={self.fps_stats.minval:04.0f}',
            f'maxfps={self.fps_stats.maxval:04.0f}',
        )
        images, rects = pygamelib.make_blitables_from_font(lines, self.font, 'azure')
        self.screen.blits(zip(images, rects))
        pygame.display.flip()


class CirclePoints(pygamelib.DemoCommand):

    command_name = 'circle_points'
    command_help = (
        'Demonstrate the circle_points function is'
        ' yielding circles in correct screen space.'
    )

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument('angles', type=pygamelib.sizetype())
        parser.add_argument('step', type=int)
        parser.add_argument('center_radius', type=int)
        parser.add_argument('radius', type=int)

    def main(self, args):
        window = pygame.Rect((0,0), args.display_size)
        font = pygamelib.monospace_font(20)
        origin = pygame.Vector2(window.center)
        angles = list(range(*args.angles, args.step))
        centers = list(
            pygamelib.circle_point(angle, args.center_radius)
            for angle in map(math.radians, angles)
        )
        circles = [pygamelib.Circle(center, args.radius) for center in centers]
        label_texts = [f'{index=}' for index, circle in enumerate(circles)]

        def _texts():
            radius = min(window.size) // 6
            for circle, label, angle in zip(circles, label_texts, angles):
                rect = pygamelib.circle_rect(circle.center, circle.radius)
                rect = pygame.Rect(rect)
                rect.center = circle.center
                text = pygamelib.Text(font, label, rect)
                yield text

        labels = list(_texts())

        shapes = circles + labels
        styles = [dict(color='red', width=1) for _ in shapes]
        shape_browser = pygamelib.ShapeBrowser(shapes, styles)
        pygame.display.set_mode(window.size)
        pygamelib.run(shape_browser)


class MeterBarHorizontalRect(pygamelib.DemoCommand):

    command_name = 'meter_bar_horizontal_rect'
    comamnd_help = 'Simple horizontal bars representing an integer.'

    def main(self, args):
        window = pygame.Rect((0,0), args.display_size)
        winwidth, winheight = window.size
        meterwidth = winwidth * .50
        meterheight = winheight * .05
        meter_rect = pygame.Rect(0, 0, meterwidth, meterheight)
        meter_rect.center = window.center
        style = dict(color='gold', width=0)
        meter = pygamelib.Meter(value=3)
        renderer = pygamelib.SimpleMeterRender(meter, meter_rect, style=style)
        shapes = [renderer]
        styles = [style]
        shape_browser = pygamelib.ShapeBrowser(shapes, styles)
        pygame.display.set_mode(window.size)
        pygamelib.run(shape_browser)


class MeterBarCircular(pygamelib.DemoCommand):

    command_name = 'meter_bar_circular'
    command_help = 'Circular arc segments representing an integer.'

    def main(self, args):
        window = pygame.Rect((0,0), args.display_size)
        meter = pygamelib.Meter(value=3, maxvalue=6)
        style = dict(
            segment_color = 'gold',
            segment_color_off = 'grey10',
            segment_width = 0,
            segment_border_width = 3,
            segment_border_color = 'orangered',
        )

        outer_radius = min(window.size) * .20
        rect = pygame.Rect(0,0,outer_radius*2,outer_radius*2)
        rect.bottomright = window.bottomright
        rect.center = window.center

        # would like to see the values "inside" all that machinery
        # especially step_for_radius
        # how many points it generates

        # TODO
        # - replace all this
        # - create the polygons
        # - associate styles with the polygons based on how filled the meter is
        renderer = pygamelib.CircularMeterRenderer(
            meter,
            center = rect.center,
            outer_radius = outer_radius,
            inner_radius = outer_radius * 0.15,
            segment_offset = 360 / (meter.maxvalue + 1),
            style = style,
        )
        shape_browser = pygamelib.ShapeBrowser([renderer], [dict(color='red', width=0)])
        pygame.display.set_mode(window.size)
        pygamelib.run(shape_browser)


class Gradient(pygamelib.DemoCommand):

    command_name = 'gradient'
    command_help = 'Color.lerp to create gradients.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument('n', type=int, help='number of rects')
        parser.add_argument('size', type=int, help='square size of rects')
        parser.add_argument('color1', help='start color')
        parser.add_argument('color2', help='end color')

    def main(self, args):
        window = pygame.Rect((0,0), args.display_size)
        shape = [
            pygamelib.Rectangle((time * args.size, 0, args.size, args.size))
            for time in range(args.n)
        ]
        # TODO
        # - move_as_one for Rectangle class and other shapes
        color1 = pygame.Color(args.color1)
        styles = [
            dict(
                width = 0,
                color = color1.lerp(args.color2, time/args.n),
            )
            for time in range(args.n)
        ]
        shape_browser = pygamelib.ShapeBrowser(shape, styles)
        pygame.display.set_mode(window.size)
        pygamelib.run(shape_browser)


class CircleSegments(
    pygamelib.DemoCommand,
    pygamelib.DemoBase,
    pygamelib.StopMixin,
):
    # TODO
    # - animating start to same value as end is not reaching the end
    command_help = 'Draw a circle segment, optionally animated.'
    animatable_names = ('radii', 'segment_range', 'closed')

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument(
            'radii',
            type = pygamelib.sizetype(),
        )
        parser.add_argument(
            'segment_range',
            type = pygamelib.sizetype(),
            help = 'Start and stop circle segment in degrees.',
        )
        parser.add_argument(
            '--step',
            type = int,
            default = 8,
            help = 'Step in degrees to draw the circle as a polygon.',
        )
        # options
        parser.add_argument(
            '--closed',
            action = 'store_true',
        )
        parser.add_argument(
            '--center',
            default = 'window.center',
        )
        pygamelib.add_animate_option(
            parser,
            help = 'Animate variables over time.',
        )
        parser.epilog = (
            f'Animatable names: {CircleSegments.animatable_names}'
        )

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()
        elif event.key == (pygame.K_r):
            # simulate first frame
            self.time = self.elapsed
            self.variables = self.initial_variables.copy()
            self.update_points()

    def update(self):
        super().update()
        self.update_points()
        self.draw()

    def update_points(self):
        self.time += self.elapsed
        pygamelib.update_variables_from_animations(
            self.animations,
            self.variables,
            self.time
        )
        radii = self.variables['radii']
        segment_start, segment_stop = self.variables['segment_range']
        # TODO
        # - evenly distribute the steps
        # draw from, assumed, smaller radius to larger radius
        items = zip(
            radii,
            (
                pygamelib.range_with_end_float(segment_start, segment_stop, +self.step),
                pygamelib.range_with_end_float(segment_stop, segment_start, -self.step),
            ),
        )
        self.points = [
            point
            for radius, degrees in items
            for point in pygamelib.circle_points(degrees, radius)
        ]
        self.points = [pygame.Vector2(self.center) + point for point in self.points]
        self.draw()

    def draw(self):
        self.screen.fill('black')
        # draw points as little circles
        for point in self.points:
            pygame.draw.circle(self.screen, 'grey15', point, 8, 1)
        # draw circle segment with polygon
        pygame.draw.polygon(self.screen, 'red', self.points, 1)
        pygame.display.flip()

    def main(self, args):
        self.window = pygame.Rect((0,0), args.display_size)
        try:
            self.center = pygamelib.sizetype()(args.center)
        except ValueError:
            self.center = eval(args.center, dict(window=self.window))

        self.step = args.step

        # put all the values under animations for consistency
        # then overwrite from command line
        varargs = vars(args)
        values = map(varargs.__getitem__, self.animatable_names)
        values = map(pygamelib.animation_tuple, values)
        self.animations = dict(zip(self.animatable_names, values))

        def map_segment_range(string):
            return map(
                pygame.Vector2,
                map(
                    tuple,
                    map(pygamelib.intargs, string)
                ),
            )

        if args.animate:
            for animate_option in args.animate:
                name, *values_and_times = animate_option
                if name not in self.animations:
                    raise ValueError(f'invalid name {name}')
                if name == 'segment_range':
                    values_and_times = (
                        # first two are two-tuples of ints
                        tuple(map_segment_range(values_and_times[:2]))
                        # last two are the normal times in milliseconds of int
                        + tuple(map(int, values_and_times[2:]))
                    )
                else:
                    values_and_times = tuple(map(int, values_and_times))
                self.animations[name] = (values_and_times[:2], values_and_times[2:])

        # initialize variables from animations
        self.time = 0
        self.variables = dict(
            pygamelib.variables_from_animations(
                self.animations,
                self.time
            )
        )
        self.initial_variables = self.variables.copy()
        self.elapsed = None
        engine = pygamelib.Engine()
        pygame.display.set_mode(self.window.size)
        engine.run(self)


class Blits(pygamelib.DemoCommand):

    command_name = 'blits'
    command_help = 'Investigating speed of `Surface.blits` and surface size.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument(
            'tile_size',
            type = pygamelib.sizetype(),
        )

    def main(self, args):
        window = pygame.Rect((0,0), args.display_size)
        font = pygamelib.monospace_font(30)
        state = BlitTilesDemo(window.size, args.tile_size, font)
        pygame.display.set_mode(window.size)
        engine = pygamelib.Engine()
        engine.run(state)


class Heart(pygamelib.DemoCommand):

    command_name = 'heart'
    command_help = 'Draw heart with arcs and lines.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument(
            '--cleft-angle',
            type = int,
            default = 45,
            help = 'Heart cleft angle in degrees.',
        )
        parser.add_argument(
            '--fraction',
            type = int,
            help = 'fraction/1000 size of window of heart.',
        )

    def main(self, args):
        window = pygame.Rect((0,0), args.display_size)
        pygame.display.init()
        pygame.font.init()

        if args.fraction:
            f = args.fraction / 1000
        else:
            f = 0 # reduce by nothing
        heart_rect = pygame.Rect(pygamelib.reduce_rect(window, f))
        heart_rect.center = window.center
        heart_shape = pygamelib.HeartShape(
            cleft_angle = args.cleft_angle,
        )
        heart = list(heart_shape(heart_rect))
        styles = list(it.repeat(
            dict(
                color = 'red',
                width = 1,
            ), 3
        ))
        state = pygamelib.ShapeBrowser(heart, styles)

        pygame.display.set_mode(window.size)
        engine = pygamelib.Engine()
        engine.run(state)


class LineLineIntersection(
    pygamelib.DemoCommand,
    pygamelib.DemoBase,
    pygamelib.SimpleQuitMixin,
    pygamelib.StopMixin,
):

    command_name = 'line_line_intersect'
    command_help =  'Demo line-line intersections.'

    def do_videoexpose(self, event):
        self.draw()

    def do_mousemotion(self, event):
        self.line2point2 = event.pos
        self.draw()

    def draw(self):
        self.screen.fill('black')
        pygame.draw.line(self.screen, 'red', *self.line1, 1)
        line2 = (self.line2point1, self.line2point2)
        pygame.draw.line(self.screen, 'red', *line2, 1)

        point = pygamelib.line_line_intersection(self.line1, line2)
        if point:
            pygame.draw.circle(self.screen, 'steelblue', point, 10)

        pygame.display.flip()

    def main(self, args):
        # this is an example of using the demo class itself as the state
        window = pygame.Rect((0,0), args.display_size)

        self.line1 = (window.topleft, window.bottomright)
        self.line2point1 = self.line2point2 = window.topright

        engine = pygamelib.Engine()
        pygame.display.set_mode(window.size)
        engine.run(self)


class DiagonalLineFill(
    pygamelib.DemoCommand,
    pygamelib.DemoBase,
    pygamelib.SimpleQuitMixin,
    pygamelib.StopMixin,
):

    command_help = 'Fill with diagonal offset lines.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument('--size', type=pygamelib.sizetype())
        parser.add_argument('--steps', type=pygamelib.sizetype(), default='8')
        parser.add_argument('--reverse', action='store_true')
        parser.add_argument('--overdraw', action='store_true')
        parser.add_argument('--color1', default='orangered')
        parser.add_argument('--color2', default='gold')

    def do_mousemotion(self, event):
        if event.buttons[0]:
            self.offset += event.rel
            self.draw_debug()

    def do_keydown(self, event):
        super().do_keydown(event)
        if event.key == pygame.K_r:
            self.reverse = not self.reverse
            self.draw_debug()
        elif event.key == pygame.K_o:
            self.overdraw = not self.overdraw
            self.draw_debug()
        elif event.key == pygame.K_RIGHT:
            self.stepx += 1
            self.draw_debug()
        elif event.key == pygame.K_LEFT:
            if self.stepx > 2:
                self.stepx -= 1
                self.draw_debug()
        elif event.key == pygame.K_UP:
            self.stepy += 1
            self.draw_debug()
        elif event.key == pygame.K_DOWN:
            if self.stepy > 2:
                self.stepy -= 1
                self.draw_debug()

    def do_videoexpose(self, event):
        self.draw_debug()
        # TODO
        # - normal draw

    def draw_debug(self):
        # debugging draw to show overdraw
        self.screen.fill('black')
        image = pygame.Surface(self.size, pygame.SRCALPHA)
        rect = image.get_rect(center=self.window.center)
        lines = list(pygamelib.rect_diagonal_lines(
            rect,
            (self.stepx, self.stepy),
            self.reverse,
            clip = not self.overdraw,
        ))
        for i, line in enumerate(lines):
            t = i / len(lines)
            color = pygame.Color(self.color1).lerp(self.color2, t)
            p1, p2 = map(lambda p: self.offset + p, line)
            pygame.draw.line(image, color, p1, p2, 1)
            pygame.draw.line(self.screen, color, p1, p2, 1)
        pygame.draw.rect(self.screen, 'red', rect.move(self.offset), 1)
        squared_rect = pygamelib.make_rect(
            rect,
            size = (sum(self.size),)*2,
        )
        pygame.draw.rect(self.screen, 'blue', squared_rect.move(self.offset), 1)

        line = map(lambda p: self.offset + p, (squared_rect.topleft, squared_rect.bottomright))
        pygame.draw.line(self.screen, 'blue', *line, 1)

        line = map(lambda p: self.offset + p, (squared_rect.topright, squared_rect.bottomleft))
        pygame.draw.line(self.screen, 'blue', *line, 1)

        # NOTES
        # - when the step slope is 0.5 it works
        # - stopping work on this to do a line gradient thing

        lines = [
            f'{self.stepx=}',
            f'{self.stepy=}',
            f'slope={self.stepy/self.stepx:=0.2f}',
            f'{self.reverse=}',
            f'{self.overdraw=}',
            f'{self.size=}',
        ]
        images, rects = pygamelib.make_blitables_from_font(lines, self.font, 'ghostwhite')
        for image, rect in zip(images, rects):
            self.screen.blit(image, rect)
        pygame.display.flip()

    def main(self, args):
        # XXX: running ourself as the demo is probably too much
        self.offset = pygame.Vector2()
        self.window = pygame.Rect((0,0), args.display_size)
        if args.size:
            self.size = args.size
        else:
            self.size = pygamelib.reduce_rect(self.window, 0.20).size
        self.stepx, self.stepy = args.steps
        self.reverse = args.reverse
        self.overdraw = args.overdraw
        self.color1 = args.color1
        self.color2 = args.color2
        engine = pygamelib.Engine()
        pygame.display.set_mode(self.window.size)
        self.font = pygamelib.monospace_font(20)
        engine.run(self)


class LineGradient(
    pygamelib.DemoCommand,
    pygamelib.DemoBase,
    pygamelib.StopMixin,
):

    #command_name = 'line_gradient'
    command_help = 'Produce a gradient along a line.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument(
            'steps',
            type = int,
            help = 'Gradient color steps.',
        )
        parser.add_argument(
            'length',
            type = int,
            help = 'Length either side of a line.',
        )
        parser.add_argument('--color1', default='orangered')
        parser.add_argument('--color2', default='gold')
        parser.add_argument('--border-color')
        parser.add_argument('--border-width', type=int, default=1)

    def main(self, args):
        gradient_line_dict = {
            key: val for key, val in vars(args).items()
            if key in ('length', 'steps')
        }
        self.variables = VariableManager(gradient_line_dict)
        self.keydown_variables = KeydownVariables(self.variables)
        self.gradient_line_renderer = GradientLineRenderer.from_dict(**gradient_line_dict)
        self.color1 = args.color1
        self.color2 = args.color2
        self.border_color = args.border_color
        self.border_width = args.border_width

        self.window = pygame.Rect((0,0), args.display_size)
        rect = pygamelib.reduce_rect(self.window, (-0.20, -0.50))
        self.line = pygamelib.Line(rect.topleft, rect.bottomright)
        engine = pygamelib.Engine()
        pygame.display.set_mode(self.window.size)
        self.font = pygamelib.monospace_font(25)
        engine.run(self)

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()
        else:
            handled = self.keydown_variables.handle_keydown(event)
            if handled:
                self.draw()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        pygame.draw.line(self.screen, 'red', *self.line, 1)
        self.gradient_line_renderer.update_from_dict(**self.variables.variables)
        self.gradient_line_renderer.draw(
            self.screen,
            self.line,
            self.color1,
            self.color2,
            self.border_color,
            self.border_width,
        )
        steps = self.variables['steps']
        length = self.variables['length']
        lines = [
            f'{steps=}',
            f'{length=}',
        ]
        images, rects = pygamelib.make_blitables_from_font(lines, self.font, 'ghostwhite')
        for image, rect in zip(images, rects):
            self.screen.blit(image, rect)
        pygame.display.flip()


class Ring(
    pygamelib.DemoCommand,
):

    command_help = 'Draw a ring or donut shape.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument('radii', type=pygamelib.sizetype())
        parser.add_argument('angles', type=pygamelib.sizetype())
        parser.add_argument('--steps', type=pygamelib.sizetype())
        parser.add_argument('--width', type=int, default=0)

    def main(self, args):
        self.window = pygame.Rect((0,0), args.display_size)

        radii = args.radii
        if args.steps:
            steps = args.steps
        else:
            steps = tuple(map(pygamelib.step_for_radius, radii))

        # TODO
        # - the edges of the circular segments do not look like they are the
        #   angles given
        angle1, angle2 = args.angles

        # points around the inner radius and then the outer
        def _range_for_flip(step, flip):
            # NOTES
            # - the flip is for tracing out a circular segment one way for a
            #   radii and then the other way for the other radii
            # - grab a copy into function namespace to avoid changing the outer
            #   context, even though they're not used otherwise
            a1 = angle1
            a2 = angle2
            if flip:
                a1, a2 = a2, a1
                step = -step
            return range(a1, a2+step, step)

        points = [
            point
            for radius, step, flip in zip(radii, steps, range(2))
            for point in pygamelib.circle_points(_range_for_flip(step, flip), radius)
        ]
        bounding = pygame.Rect(pygamelib.bounding_rect(points))
        centered = pygamelib.make_rect(bounding, center=self.window.center)
        delta = pygame.Vector2(centered.topleft) - bounding.topleft
        points = [delta + point for point in points]
        bounding = pygamelib.Rectangle(centered)
        ring_shape = pygamelib.Polygon(points)
        state = pygamelib.ShapeBrowser(
            [ring_shape, bounding],
            [
                # TODO
                # - gradient around the ring?
                dict(color='red', width=args.width),
                dict(color='blue', width=1),
            ]
        )
        engine = pygamelib.Engine()
        pygame.display.set_mode(self.window.size)
        engine.run(state)


class Bezier(pygamelib.DemoCommand):

    command_help = 'Bezier curve from control points.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument(
            'control_groups',
            nargs = '+',
            help = 'Groups of control points.',
        )
        parser.add_argument(
            'steps',
            type = int,
        )

    def main(self, args):
        self.window = pygame.Rect((0,0), args.display_size)

        control_points_groups = [
            list(map(pygamelib.sizetype(), group.split()))
            for group in args.control_groups
        ]

        steps = args.steps
        points_groups = [
            list(pygamelib.bezier_curve_points(control_points, steps))
            for control_points in control_points_groups
        ]
        shapes = [
            pygamelib.Lines(False, points) for points in points_groups
        ]
        state = pygamelib.ShapeBrowser(
            shapes,
            list(it.repeat(dict(color='blue', width=1), len(shapes))),
        )
        engine = pygamelib.Engine()
        pygame.display.set_mode(self.window.size)
        engine.run(state)


class Circularize(pygamelib.DemoCommand):

    command_help = 'Make a circle polygon between two points.'

    def main(self, args):
        # TODO
        # - actually implement circularize
        window = pygame.Rect((0,0), args.display_size)
        p1 = pygamelib.random_point(window)
        p2 = pygamelib.random_point(window)
        center = pygamelib.line_midpoint(p1, p2)
        shapes = [
            pygamelib.Circle(p1, 10),
            pygamelib.Circle(p2, 10),
            pygamelib.Circle(center, 10),
        ]
        styles = [
            dict(color='orangered', width=0),
            dict(color='orangered', width=0),
            dict(color='yellow', width=0),
        ]
        state = pygamelib.ShapeBrowser(shapes, styles)
        engine = pygamelib.Engine()
        pygame.display.set_mode(window.size)
        engine.run(state)


class Fire(
    pygamelib.DemoCommand,
    pygamelib.DemoBase,
    pygamelib.QuitKeydownMixin,
):

    command_help = 'Wiggle points on a triangle for fire.'

    def main(self, args):
        self.window = pygame.Rect((0,)*2, args.display_size)
        self.run()

    def run(self):
        engine = pygamelib.Engine()
        pygame.display.set_mode(self.window.size)
        engine.run(self)

    def draw(self):
        self.screen.fill('black')
        pygame.display.flip()


class PointsFile(
    pygamelib.DemoCommand,
):

    command_help = 'Load points from a file.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument('file', type=argparse.FileType())

    def main(self, args):
        points = list(pygamelib.points_from_file(args.file))


class XMLShapes(
    pygamelib.DemoCommand,
):
    # TODO
    # - docs
    # - load shapes from XML
    # - define animations in XML
    # - associate shapes with animations

    command_name = 'xml_shapes'
    command_help = 'Load shapes from xml.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument('file', type=argparse.FileType())

    def main(self, args):
        tree = ElementTree.parse(args.file)
        root = tree.getroot()

        shapes = pygamelib.Shapes.from_xml(root)
        print(shapes.database)
        print(shapes.shapes)

        # NOTES
        # - thinking what we need is a <document> that represents all the
        #   objects in the world
        # - we need to search it like CSS and other things
        # - we need to get the objects in it and attach or associate things
        #   with it
        # - working on deciding where animations, a thing that modifies the
        #   attributes of another thing over time, should go.


class Grid(
    pygamelib.DemoCommand,
    pygamelib.DemoBase,
    pygamelib.QuitKeydownMixin,
):

    command_help = 'Demonstrate rect arrangement in a grid.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument(
            'rects',
            nargs = '+',
            type = pygamelib.rect_type,
        )
        parser.add_argument(
            '--colattr',
            default = 'left',
            help = 'Attribute to align rects inside their grid cells.',
        )
        parser.add_argument(
            '--rowattr',
            default = 'top',
            help = 'Attribute to align rects inside their grid cells.',
        )
        parser.add_argument(
            '--columns',
            type = int,
            help =
                'Number of columns.'
                ' Default to square root of number of rects.',
        )
        parser.add_argument('--no-labels', action='store_true')

    def do_quit(self, event):
        self.engine.stop()

    def do_mousemotion(self, event):
        if event.buttons[0]:
            for _, rect in self.blits:
                rect.move_ip(event.rel)
            self.draw()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        self.screen.blits(self.blits)
        pygame.display.flip()

    def main(self, args):
        if args.columns:
            ncols = args.columns
        else:
            ncols = math.isqrt(len(args.rects))

        pygamelib.arrange_columns(args.rects, ncols, args.colattr, args.rowattr)

        font = pygamelib.monospace_font(20)
        def _render(index, rect):
            # resolve size
            if args.no_labels:
                size = rect.size
            else:
                text = 'x'.join(map(str, rect.size))
                size = tuple(map(max, zip(font.size(text), rect.size)))

            result = pygame.Surface(size, pygame.SRCALPHA)
            drawn = result.get_rect(size=rect.size, center=result.get_rect().center)
            pygame.draw.rect(result, 'red', drawn, 1)

            if not args.no_labels:
                text = font.render(text, True, 'white')
                result.blit(text, text.get_rect(center=result.get_rect().center))
            return result

        images = list(map(_render, *zip(*enumerate(args.rects))))
        self.blits = list(zip(images, args.rects))
        engine = pygamelib.Engine()
        pygame.display.set_mode(args.display_size)
        engine.run(self)


class CreateShape(
    pygamelib.DemoCommand,
    pygamelib.DemoBase,
    pygamelib.QuitKeydownMixin,
):

    command_help = 'Demonstrate creating a shape like Manim'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument('shape', choices=['circle', 'rect'])
        parser.add_argument('values', nargs='+')
        parser.add_argument('--steps', type=int, default=60)

    def main(self, args):
        window = pygame.Rect((0,)*2, args.display_size)

        if args.shape == 'rect':
            self.draw_for = self.draw_for_rects
        elif args.shape == 'circle':
            self.draw_for = self.draw_for_circles

        self.animations = []
        for shape_value in args.values:
            if args.shape == 'rect':
                rect = pygamelib.rect_type(shape_value)
                frames = [
                    list(
                        # XXX
                        # - worth bothering to make ints?
                        (tuple(map(int, start)), tuple(map(int, end)))
                        for start, end in pygamelib.trace_rect(
                            rect,
                            pygamelib.cubic_ease_in_out(i / args.steps)
                        )
                    )
                    for i in range(args.steps)
                ]
                self.animations.append(it.cycle(frames))
            elif args.shape == 'circle':
                circle = pygamelib.Circle(*pygamelib.circle_type(shape_value))
                frames = [
                    [circle.create_draw_args(i / args.steps, 1) for i in range(args.steps)]
                ]
                print(frames)
                self.animations.append(it.cycle(frames))

        self.time = 0
        engine = pygamelib.Engine()
        pygame.display.set_mode(window.size)
        engine.run(self)

    def do_quit(self, event):
        self.engine.stop()

    def update(self):
        super().update()
        self.time += self.elapsed
        self.draw()

    def draw(self):
        self.screen.fill('black')
        self.draw_for()
        pygame.display.flip()

    def draw_for_rects(self):
        for animation in self.animations:
            for line in next(animation):
                pygame.draw.line(self.screen, 'red', *line)

    def draw_for_circles(self):
        for animation in self.animations:
            for arc_args in next(animation):
                pygame.draw.arc(self.screen, 'red', *arc_args)


class PartialBorder(
    pygamelib.DemoCommand,
    pygamelib.DemoBase,
    pygamelib.QuitKeydownMixin,
):

    command_help = 'Fill the border of a rect partially and offset.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument('text')
        parser.add_argument(
            'start',
            type = float,
        )
        parser.add_argument(
            'end',
            type = float,
        )
        parser.add_argument(
            '--font-size',
            type = int,
            default = 20,
        )
        parser.add_argument(
            '--inflate',
            type = pygamelib.sizetype(),
            default = '40',
        )

    def main(self, args):
        # start and end time between 0 and 1 on the border of a rect
        self.start_time = args.start
        self.end_time = args.end
        self.step_delay = 100
        self.step_timer = 0
        # render text given on command line
        self.font = pygamelib.monospace_font(args.font_size)
        self.image = self.font.render(args.text, True, 'white')
        window = pygame.Rect((0,)*2, args.display_size)
        # rect used for centering text now and enlarged border later
        self.rect = self.image.get_rect(center=window.center)
        self.image_pos = self.rect.copy()
        self.rect.inflate_ip(args.inflate)
        # start it up
        engine = pygamelib.Engine()
        pygame.display.set_mode(args.display_size)
        engine.run(self)

    def do_quit(self, event):
        self.engine.stop()

    def update(self):
        super().update()
        self.draw()

        if self.step_timer == 0:
            self.step_timer = self.step_delay
            step = 0.005
            self.start_time = (self.start_time + step) % 1
            self.end_time = (self.end_time + step) % 1
        elif self.step_timer > 0:
            if self.step_timer - self.elapsed <= 0:
                self.step_timer = 0
            else:
                self.step_timer -= self.elapsed

    def draw(self):
        self.screen.fill('black')
        self.screen.blit(self.image, self.image_pos)
        pygame.draw.rect(self.screen, 'red', self.rect, 1)
        lines = pygamelib.lerp_rect_lines(self.rect, self.start_time, self.end_time)
        for p1, p2 in lines:
            pygame.draw.line(self.screen, 'magenta', p1, p2, 8)
        lines = (
            f'start={self.start_time:.02f}',
            f'end={self.end_time:.02f}',
        )
        images, rects = pygamelib.make_blitables_from_font(lines, self.font, 'azure')
        self.screen.blits(zip(images, rects))
        pygame.display.flip()


class CircleSegmentPermutations(
    pygamelib.DemoCommand,
    pygamelib.DemoBase,
    pygamelib.StopMixin,
    pygamelib.QuitKeydownMixin,
):

    # 2023-11-27
    # - https://quillette.com/2023/11/27/chasing-the-ice-moon/
    # - https://cdn.quillette.com/2023/11/Screenshot-2023-11-24-at-6.32.33-AM.png
    # - Thought the line and circle segments were cool and wanted to generate every
    #   permutation.
    # - pull in circlesegments.py
    # - jumped off doing that to fix CircleSegments
    # 2024-03-06
    # - class is way too big
    # - running into issues with having attributes available, like the screen
    # - lost track of original goal: generate all the patterns

    command_help = 'Generate line segments and arcs on a circle.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument(
            'circle_divisions',
            type = int,
            help = 'Number of times to divide circle.',
        )
        parser.add_argument(
            '--min-path',
            type = int,
            default = 2,
            help = 'Minimum number of points to randomly select.',
        )

    def main(self, args):
        self.min_path = args.min_path
        # NOTES
        # - thinking:
        # - randomly select a direction to go
        #   like from center out, and clockwise
        #   or outside-in, and anti-clockwise
        # - select points or paths that have some minimum number of segments
        self.window = pygame.Rect((0,0), args.display_size)
        self.center = self.window.center
        self.radius = min(args.display_size) // 3

        self.font = pygamelib.monospace_font(40)

        step = 360 // args.circle_divisions
        circle_points = pygamelib.circle_points(range(0, 360, step), self.radius)
        self.points_on_circle = [
            pygame.Vector2(self.center) + point
            for point in circle_points
        ]

        # TODO
        # - use a graph instead
        # - fix random path, it is getting locked up regularly
        print(pygamelib.graph_from_circle(self.center, self.radius, step))

        self.all_points = self.points_on_circle + [self.center]

        self.screen = pygame.display.set_mode(self.window.size)
        self.update_random_path()
        self.update_draw_commands()

        # start engine on this instance
        engine = pygamelib.Engine()
        engine.run(self)

    def update_random_path(self):
        self.start_point, self.end_point = random.sample(self.all_points, 2)
        self.path = pygamelib.random_path_circle(
            self.all_points,
            self.points_on_circle,
            self.center,
            self.start_point,
            self.end_point,
        )

    def update_draw_commands(self):
        # motivated to reduce computation and to print the arc paths but only
        # once on generation
        faint = 'grey20'
        self.draw_commands = [
            (pygame.draw.circle, self.screen, faint, self.center, self.radius, 1),
        ]
        for point in self.all_points:
            if point == self.start_point:
                color = 'purple'
            elif point == self.end_point:
                color = 'orange'
            else:
                color = faint
            self.draw_commands.append(
                (pygame.draw.line, self.screen, faint, self.center, point)
            )
            self.draw_commands.append(
                (pygame.draw.circle, self.screen, color, point, 10, 1)
            )

        width = 32
        self.draw_commands.append(
            (pygame.draw.lines, self.screen, faint, False, self.path, width)
        )

        color = 'magenta'
        width = 4
        divisor = 8
        for index, (p1, p2) in enumerate(it.pairwise(self.path)):
            if p1 in self.points_on_circle and p2 in self.points_on_circle:
                points = pygamelib.lines_arc(self.center, self.radius, p1, p2, divisor)
                arc_line = list(points)
                if len(arc_line) > 1:
                    self.draw_commands.append(
                        (pygame.draw.lines, self.screen, color, False, arc_line, width)
                    )
            else:
                self.draw_commands.append(
                    (pygame.draw.line, self.screen, color, p1, p2, width)
                )
            text_image = self.font.render(f'{index}', True, 'white')
            text_rect = text_image.get_rect(center=p1)
            self.draw_commands.append(
                (self.screen.blit, text_image, text_rect.topleft)
            )

    def do_keydown(self, event):
        super().do_keydown(event)
        if event.key == pygame.K_r:
            self.update_random_path()
            self.update_draw_commands()

    def update(self):
        super().update()
        self.draw()

    def draw(self):
        self.screen.fill('black')
        for draw_command in self.draw_commands:
            func, *funcargs = draw_command
            func(*funcargs)
        pygame.display.flip()


class TimerDemo(
    pygamelib.DemoCommand,
    pygamelib.DemoBase,
    pygamelib.StopMixin,
    pygamelib.QuitKeydownMixin,
):
    # 2024-03-10 Sun.
    # - working out a good timer
    # - started yesterday in another file
    # - was working on animate.py and animations were very difficult
    # - suspected need for timer
    # - keeping a `time` in each timer should allow for cool slowdown effects

    command_help = 'Demo the timer class.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument(
            'start',
            type = int,
            help = 'Start time in milliseconds.'
        )
        parser.add_argument(
            'duration',
            type = int,
            help = 'Duration in milliseconds.',
        )
        parser.add_argument(
            'repeat',
            type = pygamelib.repeat_type,
            help = 'Repeat N times.',
        )
        parser.add_argument(
            '--time-divisor',
            type = int,
            default = 1,
        )

    def main(self, args):
        timer = pygamelib.Timer(args.start, args.duration, args.repeat)
        self._run(args.display_size, args.framerate, timer, args.time_divisor)

    def timer_lines(self, timer):
        yield f'{timer.duration=}'
        yield f'{timer.end_stop=}'
        yield f'{timer.is_running()=}'
        yield f'{timer.is_stopped()=}'
        yield f'{timer.should_start()=}'
        yield f'{timer.should_end()=}'
        yield f'{timer.start_count=}'
        yield f'{timer.end_count=}'
        yield f'{timer.start=}'
        yield f'{timer.end=}'
        yield f'{timer.time=}'
        if timer.is_running():
            yield f'{timer.normtime()=:.6f}'
        else:
            yield '(not running)'

    def _run(self, display_size, framerate, timer, time_divisor):
        # NOTES
        # - using the run func developed in another file
        # - not sure about the Engine class and its way of running
        # - keep forgetting how to use it and I made it
        font = pygamelib.monospace_font(30)
        font_printer = pygamelib.FontPrinter(font, 'linen')
        antialias = True
        color = 'linen'
        running = True
        window = pygame.Rect((0,0), display_size)
        screen = pygame.display.set_mode(display_size)
        clock = pygame.time.Clock()
        elapsed = clock.tick(framerate)
        timer_elapsed = max(1, elapsed // time_divisor)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
            # draw
            screen.fill('black')
            lines = [
                f'fps={clock.get_fps():.2f}',
                '',
                f'{timer_elapsed=}',
            ]
            lines.extend(self.timer_lines(timer))
            image = font_printer(lines)
            screen.blit(image, image.get_rect(center=window.center))
            pygame.display.flip()
            # update
            elapsed = clock.tick(framerate)
            timer_elapsed = max(1, elapsed // time_divisor)
            timer.update(timer_elapsed)


class OverlapDemo(
    pygamelib.DemoCommand, # static parser methods
    pygamelib.DemoBase, # .start, .update
    pygamelib.StopMixin, # .do_quit
    pygamelib.QuitKeydownMixin, # .do_keydown
):
    # 2024-01-04 Thu.

    command_help = 'Demonstrate function return all overlaps.'

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument(
            'rects',
            nargs = '+',
            type = pygamelib.rect_type,
            help = 'One or more rect type arguments.',
        )
        parser.add_argument(
            '--knife',
            type = pygamelib.knife_type,
            default = '100,400',
            help = ' '.join([
                'User controllable rect.',
                pygamelib.knife_type.__doc__,
                'Default: %(default)s',
            ]),
        )
        pygamelib.add_seed_option(parser)

    def main(self, args):
        font = pygamelib.monospace_font(20)
        printer = pygamelib.FontPrinter(font, 'white')

        self.window = pygame.Rect((0,0), args.display_size)
        self.background = pygame.Surface(self.window.size)
        help_image = printer([
            'Left click to set position',
            'Space rotate',
            'A/Z increase/decrease rects',
            'Escape or Q to quit',
        ])
        self.background.blit(help_image, (0,0))

        self.rects = list(map(pygame.Rect, args.rects))
        self.knife = pygame.Rect(args.knife)
        self.rects.append(self.knife)

        population = sorted(pygamelib.UNIQUE_COLORSTHE_COLORFUL)
        self.colors = random.sample(population, len(self.rects))
        self._update_overlaps()

        self.screen = pygame.display.set_mode(self.window.size)
        engine = pygamelib.Engine()
        engine.run(self)

    def do_videoexpose(self, event):
        self.draw()

    def _knife_position(self, center):
        self.knife.center = center
        self._update_overlaps()
        self.draw()

    def _knife_flip(self):
        center = self.knife.center
        self.knife.size = tuple(reversed(self.knife.size))
        self.knife.center = center
        self._update_overlaps()
        self.draw()

    def _overlaps(self):
        for r1, r2 in it.combinations(self.rects, 2):
            if r1 is r2:
                continue
            overlap = r1.clip(r2)
            if overlap:
                yield (r1, r2, overlap)

    def _update_overlaps(self):
        self.overlaps = list(self._overlaps())

    def do_mousebuttondown(self, event):
        if event.button == pygame.BUTTON_LEFT:
            self._knife_position(event.pos)

    def do_mousemotion(self, event):
        if event.buttons[0]:
            self._knife_position(event.pos)

    def do_keydown(self, event):
        super().do_keydown(event)
        if event.key == pygame.K_SPACE:
            self._knife_flip()

    def draw(self):
        self.screen.blit(self.background, (0,0))
        #pygame.draw.rect(self.screen, 'maroon', self.knife, 1)

        rects_with_colors = list(zip(self.rects, self.colors))
        for rect, color in rects_with_colors:
            pygame.draw.rect(self.screen, color, rect, 1)

        # TODO
        # - iterate making overlaps until there are distinct overlap rects
        # - as in, what happens for more than two overlapping rects,
        #   overlapping the same area

        for r1, r2, overlap in self.overlaps:
            if r1 in self.rects:
                r1_index = self.rects.index(r1)
                r1_color = rects_with_colors[r1_index][1]
            else:
                # how the hell is it not in the list!
                r1_color = 'yellow'

            if r2 in self.rects:
                r2_index = self.rects.index(r2)
                r2_color = rects_with_colors[r2_index][1]
            else:
                r2_color = 'yellow'

            color = pygame.Color(r1_color).lerp(r2_color, 0.5)
            pygame.draw.rect(self.screen, color, overlap, 0)
        pygame.display.flip()


def filled_shape_meter(window):
    """
    Fill a shape from bottom-up as an indication of a meter.
    """
    # watching "Reigns: Game of Thrones" with MATN
    # icons at the top represent stats that change with your choices
    # they fill or drain from the bottom-up
    pass

def add_subcommands(parser, **kwargs):
    subparsers = parser.add_subparsers(help='Demo to run.')
    for demo_class in pygamelib.iterdemos(globals().values()):
        subparser_name = pygamelib.get_subcommand_name(demo_class)
        kwargs = dict()
        if hasattr(demo_class, 'command_help'):
            kwargs['help'] = demo_class.command_help
            kwargs['description'] = demo_class.command_help
        if hasattr(demo_class, 'parser_kwargs'):
            kwargs.update(demo_class.parser_kwargs())
        sp = subparsers.add_parser(subparser_name, **kwargs)
        demo_class.add_parser_arguments(sp)
        sp.set_defaults(demo_class=demo_class)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('--list', action='store_true')
    add_subcommands(parser)
    args = parser.parse_args(argv)

    if args.list:
        # print demo names and exit
        for demo_class in pygamelib.iterdemos(globals().values()):
            name = pygamelib.get_subcommand_name(demo_class)
            print(name)
        return

    demo_class = args.demo_class
    del args.demo_class
    instance = demo_class()
    instance.main(args)

if __name__ == '__main__':
    main()

# 2024-02-04 Sun.
# - want a system for quickly demonstrating functions in pygamelib
# - motivated by circle_points and getting screen space correct
