import argparse
import itertools as it
import operator as op

import pygamelib

from pygamelib import pygame

def grid_dimension(camera_pos, grid_size, window_size):
    camera_x, camera_y = map(int, camera_pos)
    grid_w, grid_h = map(int, grid_size)
    window_w, window_h = map(int, window_size)
    xs = range(camera_x % grid_w, window_w, grid_w)
    ys = range(camera_y % grid_h, window_h, grid_h)
    return it.product(xs, ys)

def lines_for_intersection(rect, point):
    x, y = point
    left, top, width, height = rect
    yield ((x, left), (x, width))
    yield ((top, y), (height, y))

def run(display_size, framerate, background, grid_size):
    pygame.font.init()
    screen = pygame.display.set_mode(display_size)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    font = pygamelib.monospace_font(20)
    font_color = 'orange'
    color = 'white'

    camera_pos = pygame.Vector2(grid_size)
    size = pygame.Vector2(window.size) + grid_size

    running = True
    while running:
        screen.fill(background)
        for screen_pos in grid_dimension(camera_pos, grid_size, size):
            label_pos = pygame.Vector2(screen_pos) - grid_size
            #
            world_pos = map(op.truediv, (screen_pos - camera_pos), grid_size)
            world_pos = tuple(map(int, world_pos))
            #
            if any(map(op.not_, world_pos)):
                # origin axis
                pygame.draw.rect(screen, 'olivedrab4', (label_pos, grid_size), 0)
            for p1, p2 in lines_for_intersection(window, screen_pos):
                pygame.draw.line(screen, color, p1, p2)
            text = str(world_pos)
            image = font.render(text, True, font_color)
            screen.blit(image, label_pos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    camera_pos += event.rel
        pygame.display.flip()
        clock.tick(framerate)

def argument_parser():
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        '--grid-size',
        type = pygamelib.sizetype(),
        default = '100,',
        help = 'Width and height of grid on screen.',
    )
    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)
    run(args.display_size, args.framerate, args.background, args.grid_size)

if __name__ == "__main__":
    main()
