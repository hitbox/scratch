import argparse
import math
import random

import pygamelib

from pygamelib import pygame

class ShapeBrowser(pygamelib.DemoBase):
    # dupe from shapebrowser.py
    # looking to see if something generic can pop out

    def __init__(self, shape, offset=None):
        # shape is iterable of object with a draw method like DrawMixin
        self.shape = shape
        if offset is None:
            offset = (0,0)
        self.offset = pygame.Vector2(offset)
        # XXX
        self.timer = 0

    def update(self):
        super().update()
        # XXX
        # wanted to see the value change and the renderer update
        self.timer = (self.timer + 1) % 20
        if self.timer == 0:
            meter = self.shape[0].meter
            meter.value = pygamelib.modo(meter.value + 1, meter.maxvalue+1, meter.minvalue)
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
        for drawable in self.shape:
            drawable.draw(self.screen, self.offset)
        pygame.display.flip()


def circle_points(window):
    """
    Demonstrate the circle_points function is yielding circles in correct
    screen space.
    """
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

    state = ShapeBrowser(circles + labels)
    pygame.display.set_mode(window.size)
    pygamelib.run(state)

def meter_bar_horizontal_rect(window):
    """
    Simple horizontal bars representing an integer.
    """
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
    state = ShapeBrowser([renderer])
    pygame.display.set_mode(window.size)
    pygamelib.run(state)

def meter_bar_circular(window):
    """
    Circular arc segments representing an integer.
    """
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
    state = ShapeBrowser([renderer])
    pygame.display.set_mode(window.size)
    pygamelib.run(state)

def circle_segments_parser():
    parser = argparse.ArgumentParser()
    # required positional
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
    pygamelib.add_animate_option(parser)
    return parser

def circle_segments(window, argv):
    """
    Draw a circle segment, optionally animated.
    """
    parser = circle_segments_parser()
    args = parser.parse_args(argv)

    try:
        center = pygamelib.sizetype()(args.center)
    except ValueError:
        center = eval(args.center)

    # put all the values under animations for consistency
    names = ('inner_radius', 'outer_radius', 'segment_offset', 'closed')
    animations = pygamelib.animations_from_options(parser, names, args.animate)
    pygamelib.setdefaults_for_animate(animations, names, args)

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

def circularize(window, args):
    """
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
    # watching "Reigns: Game of Thrones" with MATN
    # icons at the top represent stats that change with your choices
    # they fill or drain from the bottom-up
    pass

def add_subcommands(parser, **kwargs):
    subparsers = parser.add_subparsers(help='Demo to run.')
    demo_funcs = [
        circle_points,
        circle_segments,
        circularize,
        filled_shape_meter,
        meter_bar_circular,
        meter_bar_horizontal_rect,
    ]
    for func in demo_funcs:
        sp = subparsers.add_parser(func.__name__, help=func.__doc__)
        sp.set_defaults(func=func)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    add_subcommands(parser)
    known_args, remaining_args = parser.parse_known_args(argv)
    window = pygame.Rect((0,)*2, known_args.display_size)
    known_args.func(window, remaining_args)

if __name__ == '__main__':
    main()

# 2024-02-04 Sun.
# - want a system for quickly demonstrating functions in pygamelib
# - motivated by circle_points and getting screen space correct
