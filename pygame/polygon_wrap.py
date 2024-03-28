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

class State:

    def __init__(self, shapes):
        self.shapes = shapes
        self.clips = list(clippings(self.shapes))
        self.points = None
        self.edges = None
        self.lines = None

    def reset(self):
        self.points = [] # uncontained and intersection points
        self.lines = []
        self.edges = []

    def add_shape_lines(self):
        for shape in self.shapes:
            for line in shape.lines:
                self.lines.append(line)

    def bisect_intersections(self):
        lines_intersections = set()
        for line_pair in it.combinations(self.lines, 2):
            line1, line2 = line_pair
            intersection = pygamelib.line_line_intersection(line1, line2)
            if intersection:
                lines_intersections.add((line1, intersection))
                lines_intersections.add((line2, intersection))
                if line1 in self.lines:
                    self.lines.remove(line1)
                if line2 in self.lines:
                    self.lines.remove(line2)

        for line, intersection in lines_intersections:
            for point in line:
                self.lines.append((point, intersection))

    def remove_lines_with_contained_points(self):
        todo = []
        for line in self.lines:
            for point in line:
                for shape in self.shapes:
                    if shape.contains_point(point):
                        todo.append(point)

        todo = [line for point in todo for line in self.lines if point in line]
        for line in todo:
            if line in self.lines:
                self.lines.remove(line)

    def uncontained_points(self):
        for shape in self.shapes:
            for line in shape.lines:
                for point in line:
                    if not any(
                        other.contains_point(point)
                        for other in self.shapes if other != shape
                    ):
                        self.points.append(point)

    def intersection_points(self):
        for shape1, shape2 in it.product(self.shapes, repeat=2):
            if shape1 == shape2:
                continue
            for shape1_line, shape2_line in it.product(shape1.lines, shape2.lines):
                if shape1_line == shape2_line:
                    continue
                intersection = pygamelib.line_line_intersection(shape1_line, shape2_line)
                if not intersection:
                    continue
                intersection = tuple(map(int, intersection))
                if intersection not in self.points:
                    self.points.append(intersection)

    def remove_contained_points(self):
        to_remove = []
        for point in self.points:
            if any(
                other.contains_point(intersection)
                for other in self.shapes
                if other != shape1 and other != shape2
            ):
                to_remove.append(point)

        for gone in to_remove:
            self.points.remove(gone)

    def add_edge_lines(self):
        for p, q, r in it.combinations(self.points, 3):
            if (
                pygamelib.orientation(p, q, r) != 0
                and pygamelib.is_axis_aligned((q,r))
                and pygamelib.is_axis_aligned((p,q))
            ):
                self.edges.append((p, q))
                self.edges.append((q, r))


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

def alternating_distant_colors(n):
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
    colors = list(it.islice(it.cycle(colors), n))
    return colors

def clippings(shapes):
    for shape1, shape2 in it.combinations(shapes, 2):
        if (clip := shape1.clip(shape2)):
            yield clip

def run(display_size, framerate, background, shapes):
    # steps for wrapping shapes with a polygon
    algorithm = State(shapes)
    current = 0
    steps = [
        'reset',
        #'uncontained_points',
        #'intersection_points',
        #'add_edge_lines',
        'add_shape_lines',
        'bisect_intersections',
        'remove_lines_with_contained_points',
    ]
    done = set()

    font = pygamelib.monospace_font(16)
    small_font = pygamelib.monospace_font(12)
    printer = pygamelib.FontPrinter(font, 'linen')
    clock = pygame.time.Clock()
    line_index_labels = True
    running = True
    label_points = False
    colors = alternating_distant_colors(1000)
    clip_color = pygame.Color('grey50')
    clip_color.a = 255 // 5
    screen = pygame.display.set_mode(display_size)
    while running:
        current_name = steps[current]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
                elif event.key == pygame.K_SPACE:
                    if current_name not in done:
                        method = getattr(algorithm, current_name)
                        method()
                        done.add(current_name)
                elif event.key == pygame.K_RIGHT:
                    if (current_name in done and current < len(steps) - 1):
                        current += 1
        screen.fill(background)
        # render shapes
        if current == 0:
            color = 'grey50'
            width = 2
        else:
            color = 'grey20'
            width = 8
        for shape in algorithm.shapes:
            shape.draw(screen, color, width)
        if algorithm.points:
            # render points
            for point in algorithm.points:
                pygame.draw.circle(screen, 'grey50', point, 4)

            if label_points:
                texts = map(str, algorithm.points)
                images = [
                    small_font.render(text, True, 'white', 'black')
                    for text in texts
                ]
                rects = [
                    image.get_rect(center=point)
                    for image, point in zip(images, algorithm.points)
                ]
                pygamelib.resolve_rect_collisions(rects, 5)
                screen.blits(zip(images, rects))
        if algorithm.edges:
            # render edges
            for line, color in zip(algorithm.edges, colors):
                p1, p2 = line
                pygame.draw.line(screen, color, p1, p2, 1)
        if algorithm.lines:
            for line, color in zip(algorithm.lines, colors):
                p1, p2 = line
                pygame.draw.line(screen, color, p1, p2, 1)
                pygame.draw.circle(screen, color, p1, 4)
                pygame.draw.circle(screen, color, p2, 4)
        # render text
        lines = [
            f'{current}. {current_name}',
            f'{current_name in done=}',
        ]
        text_image = printer(lines)
        screen.blit(text_image, (0,0))
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
