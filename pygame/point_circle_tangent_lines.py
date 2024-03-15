import argparse
import math

import pygamelib

from pygamelib import pygame

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y


class Circle:

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius


def find_outer_tangent_lines(circle, external_point):
    # Calculate the distance between the circle's center and the external point
    distance = math.dist(external_point, circle.center)

    # Calculate the angle between the line connecting the circle's center and
    # the external point and the x-axis
    x = external_point.x - circle.center.x
    y = external_point.y - circle.center.y
    angle = math.atan2(y, x)

    # Calculate the distance from the circle's center to the midpoint of the
    # line connecting the circle's center and the external point
    mid_radius = math.sqrt(distance ** 2 - circle.radius ** 2)

    # Calculate the midpoint of the line connecting the circle's center and the
    # external point
    x = circle.center.x + mid_radius * math.cos(angle)
    y = circle.center.y + mid_radius * math.sin(angle)
    mid_point = Point(x, y)

    # Calculate the distance from the midpoint to the circle's center
    new_radius = math.sqrt(mid_radius ** 2 + circle.radius ** 2)

    # Calculate the intersection points of the new circle with the original
    # circle
    d = math.dist(circle.center, mid_point)
    if d == 0:
        return

    x = circle.radius / d
    if x < -1 or x > 1:
        return
    intersection_angle = math.asin(circle.radius / d)

    # TODO
    # - rename for points--this generates points not lines
    for intersection_angle in [+intersection_angle, -intersection_angle]:
        tangent_angle = angle + intersection_angle
        x = circle.center.x + new_radius * math.cos(tangent_angle)
        y = circle.center.y + new_radius * math.sin(tangent_angle)
        tangent_point = Point(x, y)
        yield tangent_point

def find_outer_tangent_lines(circle, point):
    # this works!
    # why doesn't the other above?
    dx = point.x - circle.center.x
    dy = point.y - circle.center.y
    d_sq = dx ** 2 + dy ** 2
    d = math.sqrt(d_sq)
    r = circle.radius

    if d_sq < r ** 2:
        # point inside the circle
        return

    angle = math.atan2(dy, dx)
    alpha = math.asin(r / d)
    beta = math.pi / 2 - alpha

    for _beta in [+beta, -beta]:
        tangent_angle = angle + _beta
        x = circle.center.x + r * math.cos(tangent_angle)
        y = circle.center.y + r * math.sin(tangent_angle)
        point = Point(x, y)
        yield point

def is_point_inside_polygon(point, polygon):
    # Compute winding number
    winding_number = 0

    for i in range(len(polygon)):
        j = (i + 1) % len(polygon)
        if (
            polygon[i].y <= point.y < polygon[j].y
            or
            polygon[j].y <= point.y < polygon[i].y
        ):
            # Compute the cross product to determine if the point is to the
            # left or right of the edge
            cross_product = (
                (polygon[j].x - polygon[i].x) * (point.y - polygon[i].y)
                -
                (point.x - polygon[i].x) * (polygon[j].y - polygon[i].y)
            )
            if cross_product > 0:
                winding_number += 1
        elif point.y == polygon[i].y and point.x > min(polygon[i].x, polygon[j].x):
            if polygon[i].y > polygon[j].y:
                winding_number += 1
        elif point.y == polygon[j].y and point.x > min(polygon[i].x, polygon[j].x):
            if polygon[j].y > polygon[i].y:
                winding_number += 1

    return winding_number % 2 == 1

def pointy_circle_polygon(circle, external_point):
    tangent_points = find_outer_tangent_lines(circle, external_point)
    tangent_points = [Point(*p) for p in tangent_points]

    triangle = tangent_points + [external_point]

    degrees = range(0, 360, 6)
    points = [
        p + tuple(circle.center)
        for p in map(
            pygame.Vector2,
            pygamelib.circle_points(degrees, circle.radius))
    ]
    # thought we needed `not is_point_inside_polygon` here
    # maybe screen space is a problem?
    points = list(filter(
        lambda p:
            is_point_inside_polygon(Point(*p), triangle),
        points
    ))
    points = [Point(*p) for p in points]
    points += triangle
    def by_angle(p):
        px, py = p
        cx, cy = circle.center
        return math.atan2(py - cy, px - cx)
    points = sorted(map(tuple, points), key=by_angle)
    return points

def run(display_size, framerate, background, circle, point):
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(display_size)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    point.x, point.y = event.pos

        # draw
        screen.fill(background)
        pygame.draw.circle(screen, 'magenta', tuple(circle.center), circle.radius, 1)
        #pygame.draw.circle(screen, 'orange', tuple(point), 2, 0)
        #for tpoint, color in zip(tangent_points, ['linen', 'grey20']):
        #    pygame.draw.line(screen, color, tuple(point), tuple(tpoint))
        points = pointy_circle_polygon(circle, point)
        if len(points) > 2:
            pygame.draw.polygon(screen, 'orange', points, 1)
        pygame.display.flip()
        clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'circle',
        type = pygamelib.circle_type,
        help = 'Space separated x y radius.'
    )
    parser.add_argument(
        'point',
        type = pygamelib.point_type,
        help = 'Space separated x y.'
    )
    args = parser.parse_args(argv)

    center, radius = args.circle
    circle = Circle(Point(*center), radius)
    point = Point(*args.point)

    run(args.display_size, args.framerate, args.background, circle, point)

if __name__ == '__main__':
    main()

# 2024-03-15 Fri.
# code cleaned up from chatgpt:
# https://chat.openai.com/c/a9e7c018-8358-468d-b7a1-a590fec5c1ee
# - want to draw a shape like a triangle joined to a circle
# - or like a circle with a pointy thing coming off it
# - thinking:
#   1. get circle.
#   2. get point.
#   3. get two lines connecting the point to the circle at the circle's
#      outermost tangent points.
#   4. get points to draw circle as polygon filtering out the points inside the
#      triangle created from the point and tangent points.
#   5. draw points as polygon.
