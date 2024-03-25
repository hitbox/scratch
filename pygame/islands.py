import argparse
import itertools as it
import random

from collections import defaultdict

import pygamelib

from pygamelib import pygame

def contains(r1, r2):
    return pygame.Rect(r1).contains(r2)

def collides(r1, r2):
    return pygame.Rect(r1).colliderect(r2)

def graph_rects(rects, is_edge=collides):
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

def run(display_size, framerate, background, rects, groups):
    group_colors = random_colorfuls(len(groups))
    rect_colors = {}
    for rect in rects:
        for index, group in enumerate(groups):
            if rect in group:
                rect_colors[rect] = group_colors[index]
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
            for rect in rects:
                color = rect_colors[rect]
                _rect = pygame.Rect(rect).move(camera)
                pygame.draw.rect(screen, color, _rect, 0)
                pygame.draw.rect(screen, color.lerp('white', 0.5), _rect, 1)
            pygame.display.flip()
            draw = False
        elapsed = clock.tick(framerate)

def argument_parser():
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'rects',
        type = argparse.FileType('r'),
        help = 'Read rects from file including stdin.',
    )
    pygamelib.add_seed_option(parser)
    return parser

def unique_paths(rects, graph):
    paths = []
    for rect in rects:
        path = tuple(depth_first_search(graph, rect))
        if set(path) not in map(set, paths):
            yield path

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)

    if args.seed:
        random.seed(args.seed)

    rects = list(map(pygamelib.rect_type, args.rects))
    graph = graph_rects(rects)
    groups = list(unique_paths(rects, graph))
    run(args.display_size, args.framerate, args.background, rects, groups)

if __name__ == '__main__':
    main()

# 2024-03-25 Mon.
# - find groups of rects where every rect has a path to every other rect
# - render the rects and color each group
