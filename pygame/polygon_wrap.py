import argparse
import itertools as it
import math
import random

from collections import defaultdict
from collections import deque

import pygamelib

from pygamelib import depth_first_search
from pygamelib import make_graph
from pygamelib import point_on_axisline
from pygamelib import pygame
from pygamelib import unique_paths

global RANDOMIZED_COLORS

class PointsShareLine:

    def __init__(self, shapes):
        self.shapes = shapes
        self.lines = [line for shape in self.shapes for line in shape.lines]

    def __call__(self, p1, p2):
        # do p1 and p2 share a line?

        # lines that p1 touches
        for line in lines_for_point(self.shapes, p1):
            # true if p2 also touches it
            if pygamelib.point_on_axisline(p2, line):
                return True


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
    # the lines that point touches
    for shape in shapes:
        for line in shape.lines:
            if pygamelib.point_on_axisline(point, line):
                yield line

def line_midpoint_in_shape(shapes, line):
    midpoint = pygamelib.line_midpoint(*line)
    for shape in shapes:
        if shape.contains_point(midpoint):
            return True

def connected_lines_for_point(shapes, point):
    for shape in shapes:
        for line in shape.lines:
            if not line_midpoint_in_shape(shapes, line):
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

def get_hulls(shapes):
    groups = grouped_shapes(shapes)
    for _shapes in groups:
        _points = list(tuple(map(int, point)) for point in uncovered_points(_shapes))
        yield _points

def render_shapes(screen, offset, shapes):
    fillcolor = pygame.Color('grey50')
    fillcolor.a = 50
    for shape in shapes:
        shape.render_onto(screen, fillcolor, 0, offset)
        shape.render_onto(screen, 'grey15', 1, offset)

def find_hover_point(hulls, event_pos):
    # broken for camera
    # unwind
    points = (point for points in hulls for point in points)
    # filter
    points = (point for point in points if math.dist(event_pos, point) < 30)
    # minimum
    return min(points, key=lambda p: math.dist(p, event_pos), default=None)

def render_points(screen, offset, hulls, font, label=False):
    for hull_points in hulls:
        for index, hull_point in enumerate(hull_points):
            pygame.draw.circle(screen, 'grey20', hull_point, 4)
            if label:
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

def render_polygon_attempt1(screen, colors, unique_paths_paths):
    items = zip(unique_paths_paths, colors)
    for unique_paths, color in items:
        for unique_path in unique_paths:
            pygame.draw.polygon(screen, color, unique_path, 1)

def line_to_rect(line):
    p1, p2 = line
    x1, y1 = p1
    x2, y2 = p2
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    if x1 == x2:
        # vertical
        return pygame.Rect(x1, y1, 1, y2 - y1)
    elif y1 == y2:
        # horizontal
        return pygame.Rect(x1, y1, x2 - x1, 1)

def render_lines_for_hover(screen, offset, hover_point, shapes):
    if not hover_point:
        return
    lines = (line for shape in shapes for line in shape.lines)
    _colors = iter(RANDOMIZED_COLORS)
    # TODO
    # - filter out line segments that go through a shape--if there is any clip at all
    # - represent line as rect of width or height == 1

    for shape in shapes:
        for line in shape.lines:
            if pygamelib.point_on_axisline(hover_point, line):
                line_sections = pygamelib.bisect_axis_line(line, hover_point)
                for line_section, color in zip(line_sections, _colors):
                    for _shape in shapes:
                        if _shape is not shape:
                            if line_to_rect(line_section).clip(_shape):
                                break
                    else:
                        pygame.draw.line(screen, color, *line_section)

def render_line_segments_for_hover(screen, offset, hover_point, line_segment_for_point):
    if not hover_point:
        return
    _colors = iter(RANDOMIZED_COLORS)
    for line, color in zip(line_segment_for_point[hover_point], _colors):
        pygame.draw.line(screen, color, *line)
        for point in line:
            pygame.draw.circle(screen, color, point, 4, 0)

def render_connected_points_for_hover(screen, offset, hover_point, graphs_for_hulls, hulls):
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
    render_hover_point(screen, offset, hover_point)

def render_hover_point(screen, offset, hover_point):
    if hover_point:
        pygame.draw.circle(screen, 'red', hover_point, 4)

def run(display_size, framerate, background, shapes):
    # hulls are lists of points that are not contained inside a shape
    # points that are corners or intersection points
    hulls = list(get_hulls(shapes))

    all_points = [point for points in hulls for point in points]
    all_lines = list(
        ((x1, y1), (x2, y2))
        for (x1, y1), (x2, y2) in it.product(all_points, all_points)
        if x1 == x2 or y1 == y2 # vertical or horizontal
    )

    line_segments = [
        line_segment
        for point, line in it.product(all_points, all_lines)
        for line_segment in pygamelib.bisect_axis_line(line, point)
        if pygamelib.point_on_axisline(point, line)
    ]

    line_segment_for_point = defaultdict(list)
    for point in all_points:
        for line in line_segments:
            if pygamelib.point_on_axisline(point, line):
                line_segment_for_point[point].append(line)

    graphs_for_hulls = [
        pygamelib.make_graph(
            nodes = points,
            is_edge = PointsShareLine(shapes),
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
        #render_lines_for_hover(screen, offset, hover_point, shapes)
        render_line_segments_for_hover(screen, offset, hover_point, line_segment_for_point)
        render_hover_point(screen, offset, hover_point)
        #render_connected_points_for_hover(screen, offset, hover_point, graphs_for_hulls, hulls)
        #render_hulls(screen, offset, hover_point, shapes, hulls)
        #render_polygon_attempt1(screen, colors, unique_paths_paths)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def connected_lines(lines):
    for line1, line2 in it.combinations(lines, 2):
        line1_p1, line1_p2 = line1
        line2_p1, lien2_p2 = line2
        if line1_p1 == line2_p2:
            # line2 --> line1
            # line1_p1 is the end point of line2
            yield (line2_p1, line2_p2, line1_p2)
        if line1_p2 == line2_p1:
            # start of line2 is the end of line1
            # line2 --> line1
            yield (line1_p1, line1_p2, line2_p2)

def resolve_connected_lines(lines):
    graph = {}
    for line in lines:
        graph[line] = []
        for other_line in lines:
            if line != other_line and do_intersect(line, other_line):
                graph[line].append(other_line)

    visited = set()
    groups = []

    for line in lines:
        if line in visited:
            continue
        group = []
        queue = deque([line])
        while queue:
            current_line = queue.popleft()
            group.append(current_line)
            visited.add(current_line)
            for neighbor in graph[current_line]:
                if neighbor not in visited:
                    queue.append(neighbor)
        groups.append(group)

    return groups

def do_intersect(line1, line2):
    # endpoints are connected
    return set(line1).intersection(line2)

def run(display_size, framerate, background, shapes):
    points = []

    for shape in shapes:
        for line in shape.lines:
            for point in line:
                if (
                    point not in points
                    and not any(
                        other.contains_point(point)
                        for other in shapes if other != shape
                    )
                ):
                    points.append(point)

    for shape1, shape2 in it.combinations(shapes, 2):
        for shape1_line, shape2_line in it.product(shape1.lines, shape2.lines):
            intersection = pygamelib.line_line_intersection(shape1_line, shape2_line)
            if intersection:
                if (
                    not any(
                        other.contains_point(intersection)
                        for other in shapes
                        if other != shape1 and other != shape2
                    )
                ):
                    points.append(intersection)

    lines = []
    for p1, p2 in it.combinations(points, 2):
        candidate = tuple(sorted((p1, p2)))
        points_on_line = tuple(p for p in points if point_on_axisline(p, candidate))
        if len(points_on_line) != 2:
            continue
        for shape in shapes:
            for line in shape.lines:
                if point_on_axisline(p1, line) and point_on_axisline(p2, line):
                    # p1 and p2 are on the same line so there's and edge to
                    # travel on
                    lines.append(candidate)

    # rendered later
    clips = [
        pygame.Rect(clip)
        for shape1, shape2 in it.combinations(shapes, 2)
        if (clip := shape1.clip(shape2))
    ]

    # remove lines that intersect with any overlaps/clips
    todo_remove = []
    for clip in clips:
        corners = set(pygamelib.corners(clip))
        for line in lines:
            p1, p2 = line
            if p1 in corners or p2 in corners:
                continue
            if any(pygamelib.line_rect_intersections(line, clip)):
                todo_remove.append(line)
            elif any(shape.contains_line(line) for shape in shapes):
                todo_remove.append(line)

    for remove_line in todo_remove:
        while remove_line in lines:
            lines.remove(remove_line)

    # fixup for integers and tuples
    lines = [tuple(tuple(map(int, point)) for point in line) for line in lines]

    graphs = resolve_connected_lines(lines)

    font = pygamelib.monospace_font(16)
    clock = pygame.time.Clock()
    line_index_labels = True
    running = True

    # create a list of colors in an order that alternates between the furthest
    # away hue
    stack = [
        color for color in RANDOMIZED_COLORS
        if pygame.Color(color).hsva[1:3] == (100, 100)
    ]
    colors = [stack.pop()]
    while stack:
        def color_dist(c):
            c = pygame.Color(c)
            last = pygame.Color(colors[-1])
            a = c.hsva[0]
            b = last.hsva[0]
            return b - a
        furthest = sorted(stack, key=color_dist)[-1]
        index = stack.index(furthest)
        furthest_color = stack.pop(index)
        colors.append(furthest_color)

    colors = list(it.islice(it.cycle(colors), len(lines)))

    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill(background)
        for clip in clips:
            x, y, w, h = clip
            image = pygame.Surface((w,h), pygame.SRCALPHA)
            color = pygame.Color('grey50')
            color.a = 255 // 5
            pygame.draw.rect(image, color, (0, 0, w, h), 0)
            screen.blit(image, (x, y))
        for point in points:
            pygame.draw.circle(screen, 'grey50', point, 8, 0)
        for shape in shapes:
            shape.draw(screen, 'grey20', 4)

        # sorted by line length
        #_lines = sorted(lines, key=lambda line: math.dist(line[0], line[1]))
        for _lines in graphs:
            for index, (line, color) in enumerate(zip(_lines, colors)):
                pygame.draw.line(screen, color, *line)
                if line_index_labels:
                    text = f'[{index}]'
                    _background = pygame.Surface(font.size(text), pygame.SRCALPHA)
                    _background.fill(pygame.Color(color).lerp('black', 0.9))
                    image = font.render(text, True, color)
                    _background.blit(image, (0,0))
                    pos = pygamelib.line_midpoint(line)
                    screen.blit(_background, _background.get_rect(center=pos))
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    pygamelib.add_shapes_from_file_arguments(parser)
    pygamelib.add_seed_option(parser)
    args = parser.parse_args(argv)

    if args.seed:
        random.seed(args.seed)

    global RANDOMIZED_COLORS
    RANDOMIZED_COLORS = list(pygamelib.UNIQUE_COLORSTHE_COLORFUL)
    random.shuffle(RANDOMIZED_COLORS)

    shapes = list(pygamelib.shapes_from_args(args))
    run(args.display_size, args.framerate, args.background, shapes)

if __name__ == '__main__':
    main()
