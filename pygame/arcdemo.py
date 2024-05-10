import math

import pygamelib

from pygamelib import pygame

class NumberPointsArc:

    def __init__(self, autoname):
        self.autoname = autoname

    def __call__(self, argument_string):
        if argument_string == self.autoname:
            return self.autoname
        else:
            return int(argument_string)


def integrand(a, b, theta):
    return math.sqrt(
        a**2 * math.sin(theta)**2
        + b**2 * math.cos(theta)**2
    )

def arc_length_ellipse(a, b, theta1, theta2, n):
    h = (theta2 - theta1) / n
    sum_integral = 0.5 * (integrand(a, b, theta1) + integrand(a, b, theta2))
    for i in range(1, n):
        sum_integral += integrand(a, b, theta1 + i * h)
    return sum_integral * h

def smooth_points_number(arc_length, solve_for=100):
    # find n points that results in arc_length/n ~= 50
    return arc_length / solve_for

def ellipse_points(center, size, npoints, angle1=None, angle2=None):
    """
    Generate points around a center for an ellipse of width and height, size;
    from angle1 to angle2.
    """
    if angle1 is None:
        angle1 = 0
    if angle2 is None:
        angle2 = math.tau
    cx, cy = center
    width, height = size
    rx = width / 2
    ry = height / 2
    j = npoints - 1
    for i in range(npoints):
        angle = angle1 + (angle2 - angle1) * i / j
        x = cx + rx * math.cos(angle)
        y = cy + ry * -math.sin(angle)
        yield (x, y)

def argument_parser():
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'rect',
        type = pygamelib.rect_type(with_pygame=True),
        help = 'Rect to draw arc inside of.',
    )
    parser.add_argument(
        'angle1',
        type = int,
        help = 'Start angle of arc in integer degrees.',
    )
    parser.add_argument(
        'angle2',
        type = int,
        help = 'End angle of arc in integer degrees.',
    )
    parser.add_argument(
        '--npoints',
        default = 'smooth',
        type = NumberPointsArc('smooth'),
        help = 'Number of points to draw polygon. Default: %(default)s.',
    )
    parser.add_argument(
        '--draw-rect',
        action = 'store_true',
        help = "Draw the arc's containing rect.",
    )
    parser.add_argument(
        '--color',
        default = 'brown',
        help = 'Color of arc polygon line.',
    )
    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)

    display_size = args.display_size
    framerate = args.framerate
    background = args.background
    rect = args.rect
    angle1 = math.radians(args.angle1)
    angle2 = math.radians(args.angle2)

    if args.npoints == 'smooth':
        a, b = sorted(rect.size, reverse=True)
        arc_length = arc_length_ellipse(a, b, angle1, angle2, n=1)
        npoints = int(smooth_points_number(arc_length))
    else:
        npoints = args.npoints

    arc_color = pygame.Color(args.color)

    polygon = list(ellipse_points(rect.center, rect.size, npoints, angle1, angle2))

    window = pygamelib.make_rect(size=display_size)
    elapsed = 0
    running = True
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(window.size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill(background)
        if args.draw_rect:
            pygame.draw.rect(screen, 'grey20', rect, 1)
            pygame.draw.line(screen, 'grey20', rect.midtop, rect.midbottom, 1)
            pygame.draw.line(screen, 'grey20', rect.midleft, rect.midright, 1)
        pygame.draw.lines(screen, arc_color, False, polygon, 1)

        pygame.display.flip()
        elapsed = clock.tick(framerate)

if __name__ == '__main__':
    main()
