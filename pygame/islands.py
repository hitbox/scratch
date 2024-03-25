import argparse
import itertools as it
import random

from collections import defaultdict

import pygamelib

from pygamelib import pygame

def graph_shapes(rects, is_edge):
    graph = defaultdict(list)
    # make all the rects appear in the graph
    for rect in rects:
        graph[rect]
    for r1, r2 in it.combinations(rects, 2):
        if is_edge(r1, r2):
            graph[r1].append(r2)
            graph[r2].append(r1)
    return graph

def depth_first_search(graph, start):
    visited = set()
    stack = [start]
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        yield current
        visited.add(current)
        for neighbor in reversed(graph[current]):
            if neighbor in visited:
                continue
            stack.append(neighbor)

def random_colorfuls(n):
    colorfuls = map(pygame.Color, pygamelib.UNIQUE_COLORSTHE_COLORFUL)
    colorfuls = it.cycle(colorfuls)
    colorfuls = list(it.islice(colorfuls, n))
    colorfuls = random.sample(colorfuls, n)
    return colorfuls

def run(display_size, framerate, background, shapes, groups, draw_func, move_func):
    group_colors = random_colorfuls(len(groups))
    shape_colors = {}
    for shape in shapes:
        for index, group in enumerate(groups):
            if shape in group:
                shape_colors[shape] = group_colors[index]
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.set_mode(display_size)
    camera = pygame.Vector2()
    draw = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                camera += event.rel
                draw = True
        if draw:
            screen.fill(background)
            for shape in shapes:
                color = shape_colors[shape]
                _shape = move_func(shape, camera)
                draw_func(screen, color, _shape, 0)
                draw_func(screen, color.lerp('white', 0.5), _shape, 0)
            pygame.display.flip()
            draw = False
        elapsed = clock.tick(framerate)

def argument_parser():
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'shapes',
        type = argparse.FileType('r'),
        help = 'Read shapes from file including stdin.',
    )
    subparsers = parser.add_argument(
        'type',
        choices = ['circle', 'rect'],
    )
    pygamelib.add_seed_option(parser)
    return parser

def unique_paths(shapes, graph):
    paths = []
    for shape in shapes:
        path = tuple(depth_first_search(graph, shape))
        if set(path) not in map(set, paths):
            yield path

def funcs_for_circle():
    type_func = pygamelib.circle_type
    collides = pygamelib.circle_collision

    def draw(surf, color, shape, border):
        (x, y), radius = shape
        return pygame.draw.circle(surf, color, (x, y), radius, border)

    def move(shape, camera):
        dx, dy = camera
        (x, y), radius = shape
        return ((x + dx, y + dy), radius)

    return locals()

def funcs_for_rect():
    type_func = pygamelib.rect_type
    collides = pygamelib.rect_collision

    def draw(surf, color, shape, border):
        return pygame.draw.rect(surf, color, shape, border)

    def move(shape, camera):
        dx, dy = camera
        (x, y, w, h) = shape
        return (x + dx, y + dy, w, h)

    return locals()

def funcs_for_shape(type_):
    if type_ == 'circle':
        funcs = funcs_for_circle()
    elif type_ == 'rect':
        funcs = funcs_for_rect()
    return funcs

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)

    if args.seed:
        random.seed(args.seed)

    funcsdict = funcs_for_shape(args.type)
    type_func = funcsdict['type_func']
    collides = funcsdict['collides']
    draw = funcsdict['draw']
    move = funcsdict['move']

    shapes = list(map(type_func, args.shapes))
    graph = graph_shapes(shapes, collides)

    groups = list(unique_paths(shapes, graph))
    run(args.display_size, args.framerate, args.background, shapes, groups, draw, move)

if __name__ == '__main__':
    main()

# 2024-03-25 Mon.
# - find groups of rects where every rect has a path to every other rect
# - render the rects and color each group
# - later added circles
