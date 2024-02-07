import abc
import argparse
import itertools as it
import math
import random

import pygamelib

from pygamelib import pygame

class Demo(abc.ABC):

    @property
    @abc.abstractmethod
    def command_name(self):
        ...

    @staticmethod
    @abc.abstractmethod
    def parser_kwargs():
        ...

    @staticmethod
    def add_parser_arguments(parser):
        ...


class Stat:

    def __init__(self):
        self.minval = +math.inf
        self.maxval = -math.inf

    def update(self, value):
        if value < self.minval:
            self.minval = value
        if value > self.maxval:
            self.maxval = value


class BlitsDemo(pygamelib.DemoBase):

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

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()

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


class ShapeBrowser(pygamelib.DemoBase):
    # dupe from shapebrowser.py
    # looking to see if something generic can pop out

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
            pygamelib.post_quit()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        for drawable, style in zip(self.drawables, self.styles):
            color = style['color']
            width = style['width']
            drawable.draw(self.screen, color, width, self.offset)
        pygame.display.flip()


class CirclePoints(Demo):

    command_name = 'circle_points'

    @staticmethod
    def parser_kwargs():
        return dict(
            help =
                'Demonstrate the circle_points function is yielding circles'
                ' in correct screen space.',
        )

    @staticmethod
    def add_parser_arguments(parser):
        pass

    def __call__(self, window):
        font = pygamelib.monospace_font(20)

        origin = pygame.Vector2(window.center)
        angles = []
        def _centers():
            # centers of circles going around the center of the window
            radius = min(window.size) // 8
            # TODO fix for circle_point
            for angle in map(math.radians, range(0, 360, 30)):
                center = pygamelib.circle_point(window.center, radius, angle)
                yield center
                angles.append(angle)

        radius = min(window.size) // 64
        circles = [pygamelib.Circle(center, radius)  for center in _centers()]
        label_texts = [f'{index=}' for index, circle in enumerate(circles)]

        def _texts():
            radius = min(window.size) // 6
            for circle, label, angle in zip(circles, label_texts, angles):
                rect = pygamelib.circle_rect(circle.center, circle.radius)
                rect = pygame.Rect(rect)
                # TODO fix for circle_point
                rect.center = pygamelib.circle_point(origin, radius, angle)
                text = pygamelib.Text(font, label, rect)
                yield text

        labels = list(_texts())

        shape_browser = ShapeBrowser(circles + labels)
        pygame.display.set_mode(window.size)
        pygamelib.run(shape_browser)


class MeterBarHorizontalRect(Demo):

    command_name = 'meter_bar_horizontal_rect'

    @staticmethod
    def parser_kwargs():
        return dict(
            help = 'Simple horizontal bars representing an integer.',
        )

    @staticmethod
    def add_parser_arguments(parser):
        pass

    def __call__(self, window):
        winwidth, winheight = window.size
        meterwidth = winwidth * .50
        meterheight = winheight * .05
        meter_rect = pygame.Rect(0, 0, meterwidth, meterheight)
        meter_rect.center = window.center
        style = dict(
            border_color = 'lightcoral',
            border_width = 1,
            segment_margin = (0, 10),
            segment_color = 'gold',
            segment_color_off = 'grey10',
            segment_width = 0,
            segment_border = 1,
        )
        meter = pygamelib.Meter(value=3)
        renderer = pygamelib.SimpleMeterRender(meter, meter_rect, style=style)
        shape_browser = ShapeBrowser([renderer])
        pygame.display.set_mode(window.size)
        pygamelib.run(shape_browser)


class MeterBarCircular(Demo):

    command_name = 'meter_bar_circular'

    @staticmethod
    def parser_kwargs():
        return dict(
            help = 'Circular arc segments representing an integer.',
        )

    @staticmethod
    def add_parser_arguments(parser):
        pass

    def __call__(self, window):
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

        renderer = pygamelib.CircularMeterRenderer(
            meter,
            center = rect.center,
            outer_radius = outer_radius,
            inner_radius = outer_radius * 0.15,
            segment_offset = 360 / (meter.maxvalue + 1),
            style = style,
        )
        shape_browser = ShapeBrowser([renderer])
        pygame.display.set_mode(window.size)
        pygamelib.run(shape_browser)


class Gradient(Demo):

    command_name = 'gradient'

    @staticmethod
    def parser_kwargs():
        return dict(
            help = 'Color.lerp to create gradients.',
        )

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument('n', type=int, help='number of rects')
        parser.add_argument('size', type=int)
        parser.add_argument('color1')
        parser.add_argument('color2')

    def __call__(self, window):
        shape = [
            pygamelib.Rectangle(
                (
                    100 + time * args.size,
                    100,
                    args.size,
                    args.size,
                )
            )
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
        shape_browser = ShapeBrowser(shape, styles)
        pygame.display.set_mode(window.size)
        pygamelib.run(shape_browser)

class CircleSegments(Demo):

    command_name = 'circle_segments'

    @staticmethod
    def parser_kwargs():
        return dict(
            help = 'Draw a circle segment, optionally animated.',
        )

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument('inner_radius', type=int)
        parser.add_argument('outer_radius', type=int)
        parser.add_argument(
            'segment_offset',
            type = int,
            help = 'Either side offset in degrees of each circle segment.',
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

    def __call__(self, args):
        window = pygame.Rect((0,0), args.display_size)
        try:
            center = pygamelib.sizetype()(args.center)
        except ValueError:
            center = eval(args.center)

        # put all the values under animations for consistency
        varargs = vars(args)
        names = ('inner_radius', 'outer_radius', 'segment_offset', 'closed')
        animations = {name: pygamelib.animation_tuple(varargs[name]) for name in names}

        if args.animate:
            for animate_option in args.animate:
                name, *values_and_times = animation
                if name not in animations:
                    raise ValueError(f'invalid name {name}')
                values_and_times = tuple(map(int, values_and_times))
                animations[name] = (values_and_times[:2], values_and_times[2:])

        # initialize variables from animations
        time = 0
        variables = dict(pygamelib.variables_from_animations(animations, time))
        initial_variables = variables.copy()

        # TODO
        # - take two points inside the points list
        # - give a center and radius and circularize inplace
        # motivation:
        # - round over the circle segment ends

        clock = pygame.time.Clock()
        framerate = 60
        running = True
        screen = pygame.display.set_mode(window.size)
        while running:
            elapsed = clock.tick(framerate)
            time += elapsed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        pygamelib.post_quit()
                    elif event.key == (pygame.K_r):
                        time = elapsed # simulate first frame
                        variables = initial_variables.copy()
            # update
            pygamelib.update_variables_from_animations(animations, variables, time)
            points = pygamelib.circle_segment_points(
                0,
                math.radians(variables['segment_offset']),
                (variables['inner_radius'], variables['outer_radius']),
                closed = variables['closed'],
            )
            points = [pygame.Vector2(center) + point for point in points]
            # draw
            screen.fill('black')
            # draw points as little circles
            for point in points:
                pygame.draw.circle(screen, 'grey15', point, 8, 1)
            # draw circle segment with polygon
            pygame.draw.polygon(screen, 'red', points, 1)
            pygame.display.flip()


class Blits(Demo):

    command_name = 'blits'

    @staticmethod
    def parser_kwargs():
        return dict(
            help = 'Investigating speed of `Surface.blits` and surface size.',
        )

    @staticmethod
    def add_parser_arguments(parser):
        parser.add_argument(
            'tile_size',
            type = pygamelib.sizetype(),
        )

    def __call__(self, args):
        window = pygame.Rect((0,0), args.display_size)
        font = pygamelib.monospace_font(30)
        state = BlitsDemo(window.size, args.tile_size, font)
        pygame.display.set_mode(window.size)
        engine = pygamelib.Engine()
        engine.run(state)


def circularize(window, args):
    """
    Make a circle polygon between two points.
    """
    p1 = pygamelib.random_point(window)
    p2 = pygamelib.random_point(window)
    center = pygamelib.line_midpoint(p1, p2)

    angle = math.atan2(p2.y - p1.y, p2.x - p1.x)

    clock = pygame.time.Clock()
    framerate = 60
    running = True
    screen = pygame.display.set_mode(window.size)
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill('black')
        pygame.draw.circle(screen, 'orangered', p1, 10)
        pygame.draw.circle(screen, 'orangered', p2, 10)
        pygame.draw.circle(screen, 'yellow', center, 10)
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
    demos = [
        Blits,
        CirclePoints,
        CircleSegments,
        Gradient,
        MeterBarCircular,
        MeterBarHorizontalRect,
    ]
    for demo_class in demos:
        sp = subparsers.add_parser(
            demo_class.command_name,
            **demo_class.parser_kwargs()
        )
        demo_class.add_parser_arguments(sp)
        sp.set_defaults(func=demo_class())

def main(argv=None):
    parser = pygamelib.command_line_parser()
    add_subcommands(parser)
    args = parser.parse_args(argv)
    func = args.func
    del args.func
    func(args)

if __name__ == '__main__':
    main()

# 2024-02-04 Sun.
# - want a system for quickly demonstrating functions in pygamelib
# - motivated by circle_points and getting screen space correct
