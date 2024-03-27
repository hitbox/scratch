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

def points_on_line(points, line):
    for point in points:
        if pygamelib.point_on_axisline(point, line):
            yield point

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

def groups_from_shapes(shapes, clips):
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

    groups = resolve_connected_lines(lines)
    return groups

def blit_rect(surf, color, rect):
    # for transparency
    x, y, w, h = rect
    image = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.rect(image, color, (0, 0, w, h), 0)
    return surf.blit(image, (x, y))

def blit_label(surf, bgcolor, fgcolor, font, text, center):
    # TODO
    # - transparency not working
    image = font.render(text, True, fgcolor, bgcolor)
    return surf.blit(image, image.get_rect(center=center))

def color_with_alpha(color, alpha):
    color = pygame.Color(color)
    color.a = alpha
    return color

def run(display_size, framerate, background, shapes):

    # rendered later
    clips = [
        pygame.Rect(clip)
        for shape1, shape2 in it.combinations(shapes, 2)
        if (clip := shape1.clip(shape2))
    ]

    graphs = groups_from_shapes(shapes, clips)

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

    colors = list(it.islice(it.cycle(colors), sum(map(len, graphs))))
    points = [point for group in graphs for line in group for point in line]

    clip_color = pygame.Color('grey50')
    clip_color.a = 255 // 5

    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill(background)
        # partially transparent clipping regions
        for clip in clips:
            blit_rect(screen, clip_color, clip)
        for point in points:
            pygame.draw.circle(screen, 'grey50', point, 8, 0)
        for shape in shapes:
            shape.draw(screen, 'grey20', 4)
        for _lines in graphs:
            for index, (line, color) in enumerate(zip(_lines, colors)):
                pygame.draw.line(screen, color, *line)
                if line_index_labels:
                    text = f'[{index}]'
                    blit_label(
                        screen,
                        color_with_alpha(background, 75),
                        color,
                        font,
                        text,
                        pygamelib.line_midpoint(line),
                    )
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
