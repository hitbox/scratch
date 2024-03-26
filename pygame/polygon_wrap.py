import argparse
import itertools as it
import math
import random

import pygamelib

from pygamelib import depth_first_search
from pygamelib import make_graph
from pygamelib import pygame

def uncovered_points(shapes):
    for shape in shapes:
        for point in shape.points:
            others = (other for other in shapes if other != shape)
            if not any(other.contains_point(point) for other in others):
                # we've got a corner point that is not entirely contained by
                # another shape
                yield point

    for shape1, shape2 in it.combinations(shapes, 2):
        for point in shape1.intersections(shape2):
            others = (other for other in shapes if other not in (shape1, shape2))
            if not any(other.inside_point(point) for other in others):
                yield point

def orientation(p, q, r):
    px, py = p
    qx, qy = q
    rx, ry = r
    val = (qy - py) * (rx - qx) - (qx - px) * (ry - qy)
    if val == 0:
        return 0 # collinear
    elif val > 0:
        return 1 # clockwise
    else:
        return 2 # anticlockwise

def convex_hull(points):
    n = len(points)
    if n < 3:
        return

    # find the leftmost point
    leftmost_index = min(range(n), key=lambda index: points[index][0])
    p = leftmost_index
    q = 0
    while True:
        yield points[p]
        q = (p + 1) % n
        for i in range(n):
            if orientation(points[p], points[i], points[q]) == 2:
                q = i
        p = q
        if p == leftmost_index:
            break

def screen_polar_angle(p, q):
    px, py = p
    qx, qy = q
    return math.atan2(-qy - -py, qx - px)

def tight_convex_hull(points):
    n = len(points)
    if n < 3:
        return

    def compare(p1, p2):
        o = orientation(points[0], p1, p2)
        if o == 0:
            return (
                (p1[0] - points[0][0]) ** 2
                +
                (p1[1] - points[0][1]) ** 2
                -
                (
                    (p2[0] - points[0][0]) ** 2
                    +
                    (p2[1] - points[0][1]) ** 2
                )
            )
        return -1 if o == 2 else 1

    points = sorted(points, key=lambda point: (point[1], point[0]))

    # remove collinear points
    stack = [points[0]]
    for i in range(1, n):
        while len(stack) > 1 and orientation(stack[-2], stack[-1], points[i]) == 0:
            stack.pop()
        stack.append(points[i])

    points = stack

    if len(points) < 3:
        for point in points:
            yield point
        return

    # apply Graham Scan
    hull = [points[0], points[1]]
    for i in range(2, len(points)):
        while len(hull) > 1 and orientation(hull[-2], hull[-1], points[i]) != 2:
            hull.pop()
        hull.append(points[i])

    for point in hull:
        yield point

def lines_for_point(shapes, point):
    for shape in shapes:
        for line in shape.lines:
            if pygamelib.point_on_axisline(point, line):
                yield line

def points_on_line(points, line):
    for point in points:
        if pygamelib.point_on_axisline(point, line):
            yield point

def grouped_shapes(shapes):
    def is_edge(shape1, shape2):
        return shape1.collides(shape2)
    graph = pygamelib.make_graph(shapes, is_edge)
    groups = list(pygamelib.unique_paths(graph))
    return groups

def get_hulls(shapes):
    groups = grouped_shapes(shapes)
    for _shapes in groups:
        _points = list(tuple(map(int, point)) for point in uncovered_points(_shapes))
        yield _points

def render_shapes(screen, offset, shapes):
    for shape in shapes:
        shape.draw(screen, 'grey10', 0, offset)
        shape.draw(screen, 'grey15', 1, offset)

def find_hover_point(hulls, event_pos):
    # broken for camera
    for _point in (point for points in hulls for point in points):
        if math.dist(event_pos, _point) < 30:
            return _point

def render_points(screen, offset, hulls, font):
    for hull_points in hulls:
        for index, hull_point in enumerate(hull_points):
            pygame.draw.circle(screen, 'grey20', hull_point, 4)
            image = font.render(f'{index}', True, 'linen')
            screen.blit(image, image.get_rect(center=hull_point))

def render_connected_points(
    screen,
    offset,
    shapes,
    hover_point,
    hull_points,
    hull_point,
):
    connected_lines = list(lines_for_point(shapes, hover_point))
    for connected_line in connected_lines:
        pygame.draw.line(screen, 'blue', *connected_line)

    connected_points = [
        connected_point
        for connected_line in connected_lines
        for connected_point in points_on_line(hull_points, connected_line)
        if connected_point != hover_point
    ]

    for p, q in it.combinations(connected_points, 2):
        if orientation(p, hull_point, q) != 0:
            for connected_point in [p, q]:
                pygame.draw.circle(screen, 'white', connected_point, 6)
            break

def render_hulls(screen, offset, hover_point, shapes, hulls):
    # deliberately not using offset yet
    for hull_points in hulls:
        for hull_point in hull_points:
            if hull_point == hover_point:
                color = 'red'
            else:
                color = 'grey20'
            # draw hull point
            pygame.draw.circle(screen, color, hull_point, 4)
            if hover_point:
                render_connected_points(
                    screen,
                    offset,
                    shapes,
                    hover_point,
                    hull_points,
                    hull_point,
                )

class PointsShareLine:

    def __init__(self, shapes):
        self.shapes = shapes

    def __call__(self, p1, p2):
        for line in lines_for_point(self.shapes, p1):
            if pygamelib.point_on_axisline(p2, line):
                return True
        for line in lines_for_point(self.shapes, p2):
            if pygamelib.point_on_axisline(p1, line):
                return True


def render_polygon_attempt1(screen, colors, unique_paths_paths):
    items = zip(unique_paths_paths, colors)
    for unique_paths, color in items:
        for unique_path in unique_paths:
            pygame.draw.polygon(screen, color, unique_path, 1)

def render_connected_hover(screen, offset, hover_point, graphs_for_hulls, hulls):
    if hover_point is None:
        return
    for hull_points, graph in zip(hulls, graphs_for_hulls):
        if hover_point not in hull_points:
            continue
        connected_points = sorted(
            graph[hover_point],
            key=lambda p: math.dist(p, hover_point)
        )
        for point in connected_points[:2]:
            pygame.draw.circle(screen, 'blue', point, 8)
    pygame.draw.circle(screen, 'red', hover_point, 4)

def run(display_size, framerate, background, shapes):
    hulls = list(get_hulls(shapes))

    graphs_for_hulls = [
        pygamelib.make_graph(
            points,
            PointsShareLine(shapes),
        )
        for points in hulls
    ]
    for graph in graphs_for_hulls:
        for point in graph:
            connected_points = graph[point]
            connected_points.sort(
                key = lambda p: math.dist(p, point)
            )

    unique_paths_paths = [
        tuple(pygamelib.unique_paths(graph)) for graph in graphs_for_hulls
    ]
    population = list(pygamelib.UNIQUE_COLORSTHE_COLORFUL)
    colors = random.sample(population, len(unique_paths_paths))

    hover_point = None
    clock = pygame.time.Clock()
    running = True
    offset = pygame.Vector2()
    font = pygamelib.monospace_font(20)
    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    #offset += event.rel
                    pass
                elif not any(event.buttons):
                    hover_point = find_hover_point(hulls, event.pos)
        screen.fill(background)
        render_shapes(screen, offset, shapes)
        render_points(screen, offset, hulls, font)
        render_connected_hover(screen, offset, hover_point, graphs_for_hulls, hulls)
        #render_hulls(screen, offset, hover_point, shapes, hulls)
        #render_polygon_attempt1(screen, colors, unique_paths_paths)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    pygamelib.add_shapes_from_file_arguments(parser)
    pygamelib.add_seed_option(parser)
    args = parser.parse_args(argv)

    if args.seed:
        random.seed(args.seed)

    shapes = list(pygamelib.shapes_from_args(args))
    run(args.display_size, args.framerate, args.background, shapes)

if __name__ == '__main__':
    main()
