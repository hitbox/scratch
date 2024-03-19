import math

import pygamelib

from pygamelib import outer_tangent_angles
from pygamelib import pygame

class Variables:

    def __init__(self, *names, formatters=None):
        self.names = tuple(names)
        if formatters is None:
            formatters = {}
        self.formatters = formatters

    def from_dict(self, d):
        lines = ((key, val) for key, val in d.items() if key in self.names)
        lines = sorted(lines, key=lambda item: self.names.index(item[0]))
        for key, val in lines:
            if key in self.formatters:
                val = self.formatters[key](val)
            yield f'{key}={val}'


def position_for_label(label_image, point, center, margin=0):
    px, py = point
    cx, cy = center
    angle = math.atan2(py - cy, px - cx)
    radius = math.dist(center, point)
    radius += max(label_image.get_size()) / 2
    radius += margin
    x = cx + math.cos(angle) * radius
    y = cy + math.sin(angle) * radius
    return (x, y)

def circle_point(center, radius, angle):
    # XXX
    # - decide between this and the same function in pygamelib
    # - plus or minus the sin/y part
    cx, cy = center
    x = cx + math.cos(angle) * radius
    y = cy + math.sin(angle) * radius
    return (x, y)

def generate_angles(a1, a2, n):
    for i in range(n+1):
        yield pygamelib.mixangle_longest(a2, a1, i / n)

def generate_points(center, radius, angles):
    for angle in angles:
        yield circle_point(center, radius, angle)

def origin_lines(center, inside):
    cx, cy = center
    left, top, right, bottom = inside
    # horizontal
    yield ((left, cy), (right, cy))
    # vertical
    yield ((cx, top), (cx, bottom))

def points_around_circle(center, radius, point, divisions):
    # NOTE
    # - function exists to separate the essence of this demo
    # - thinking about how to render these little circles with a point sometime
    #   in the future
    a1, a2 = tuple(outer_tangent_angles(center, radius, point))
    points = [point]
    tween_angles = generate_angles(a1, a2, divisions)
    points.extend(generate_points(center, radius, tween_angles))
    return points

def draw_background_elements(soup):
    variables = soup['variables']
    printer = soup['printer']
    screen = soup['screen']
    center = soup['center']
    radius = soup['radius']
    window = soup['window']
    center_to_point_angle = soup['center_to_point_angle']
    # origin axis lines
    for p1, p2 in origin_lines(center, window):
        pygame.draw.line(screen, 'grey20', p1, p2)
    # the circle
    pygame.draw.circle(screen, 'grey20', center, radius, 1)
    # debugging: calculated line from center toward cursor
    calculated_point_on_circle = circle_point(center, radius, center_to_point_angle)
    pygame.draw.line(screen, 'darkslateblue', center, calculated_point_on_circle)
    # print variables
    lines = tuple(variables.from_dict(soup))
    if lines:
        image = printer(lines)
        screen.blit(image, (0,0))

def draw_foreground_elements(soup):
    font_renderer = soup['font_renderer']
    screen = soup['screen']
    center = soup['center']
    point = soup['point']
    points = soup['points']
    # draw polygon, the pointy circle
    if len(points) > 2:
        pygame.draw.polygon(screen, 'brown', points, 4)
    # draw labels
    point_labels = tuple(map(font_renderer, map(str, range(len(points)))))
    label_positions = tuple(
        image.get_rect(
            center = position_for_label(
                image,
                _point,
                center,
                margin = 10,
            ),
        )
        for image, _point in zip(point_labels, points)
    )
    screen.blits(tuple(zip(point_labels, label_positions)))
    # draw dots for points
    for _point in points:
        pygame.draw.circle(screen, 'linen', _point, 3)
    # point at cursor
    pygame.draw.circle(screen, 'yellow', point, 3)

def draw(soup):
    # clear
    background = soup['background']
    screen = soup['screen']
    screen.fill(background)
    draw_background_elements(soup)
    draw_foreground_elements(soup)

def run(
    display_size,
    framerate,
    background,
    divisions,
    center = None,
    radius = None,
):
    short_float = '{:.2f}'.format
    variables = Variables(
        'frames_per_second',
        'center_to_point_angle',
        'tangent_angles',
        formatters = {
            'frames_per_second': short_float,
            'center_to_point_angle': short_float,
            'tangent_angles': lambda angles: tuple(map(short_float, angles)),
        },
    )
    font = pygamelib.monospace_font(20)
    font_renderer = pygamelib.FontRenderer(font, 'linen')
    printer = pygamelib.FontPrinter(font, 'linen')
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.set_mode(display_size)
    pygame.mouse.set_visible(False)
    point = pygame.mouse.get_pos()
    window = screen.get_rect()
    if center is None:
        center = window.center
    if radius is None:
        radius = window.width // 12
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEMOTION:
                point = event.pos
        # update
        frames_per_second = clock.get_fps()
        center_to_point_angle = pygamelib.angle_to(center, point)
        # create tangent angles
        if math.dist(center, point) >= radius:
            points = points_around_circle(center, radius, point, divisions)
        else:
            tangent_angles = tuple()
            points = tuple()
        # draw
        draw(locals())
        pygame.display.flip()
        clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        '--center',
        type = pygamelib.point_type,
        help = 'Center of circle. Default: window.center.',
    )
    parser.add_argument(
        '--radius',
        type = int,
        help = 'Radius of circle. Default: 1/12 of window.width.',
    )
    parser.add_argument(
        '--divisions',
        type = int,
        default = 10,
        help = 'Number of divisions between tangent points. Default: %(default)s',
    )
    args = parser.parse_args(argv)
    run(
        args.display_size,
        args.framerate,
        args.background,
        args.divisions,
        args.center,
        args.radius,
    )

if __name__ == '__main__':
    main()

# 2024-03-17 Sun.
# - working out how to take a point outside a circle and wrap polygon around
#   the point and the circle.
# - late Sunday finally beat my head against this until it did what I want.
