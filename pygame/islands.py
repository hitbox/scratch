import argparse
import itertools as it
import random

from collections import defaultdict

import pygamelib

from pygamelib import depth_first_search
from pygamelib import make_graph
from pygamelib import pygame

def render(screen, camera, render_items):
    for group, fillcolor, bordercolor in render_items:
        for shape in group:
            shape.draw(screen, fillcolor, 0, camera)
            shape.draw(screen, bordercolor, 1, camera)

def run(display_size, framerate, background, groups):
    # colors index-aligned with shapes
    fillcolors = pygamelib.random_colorfuls(len(groups))
    bordercolors = [color.lerp('white', 0.5) for color in fillcolors]
    render_items = tuple(zip(groups, fillcolors, bordercolors))
    clock = pygame.time.Clock()
    running = True
    draw = True
    offset = pygame.Vector2()
    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                offset += event.rel
                draw = True
        if draw:
            screen.fill(background)
            render(screen, offset, render_items)
            pygame.display.flip()
            draw = False
        elapsed = clock.tick(framerate)

def grouped_shapes_from_args(args):
    shapes = list(pygamelib.shapes_from_args(args))

    def is_edge(shape1, shape2):
        return shape1.collides(shape2)

    graph = pygamelib.make_graph(shapes, is_edge)
    groups = list(pygamelib.unique_paths(graph))
    return groups

def main(argv=None):
    parser = pygamelib.command_line_parser()
    pygamelib.add_shapes_from_file_arguments(parser)
    pygamelib.add_seed_option(parser)
    args = parser.parse_args(argv)

    if args.seed:
        random.seed(args.seed)

    groups = grouped_shapes_from_args(args)
    run(args.display_size, args.framerate, args.background, groups)

if __name__ == '__main__':
    main()

# 2024-03-25 Mon.
# - find groups of rects where every rect has a path to every other rect
# - render the rects and color each group
# - later added circles
