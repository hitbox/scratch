import argparse
import itertools as it

import pygamelib

from pygamelib import pygame

def grid_dimension(camera_pos, grid_size, window_size):
    camera_x, camera_y = camera_pos
    window_w, window_h = window_size
    xs = range(camera_x % grid_size, window_w, grid_size)
    ys = range(camera_y % grid_size, window_h, grid_size)
    return it.product(xs, ys)

def run(display_size, framerate, grid_size):
    pygame.font.init()
    screen = pygame.display.set_mode(display_size)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    font = pygamelib.monospace_font(12)

    camera_pos = [0, 0]
    window_width, window_height = window.size
    color = 'white'

    running = True
    while running:
        screen.fill('black')

        for screen_grid_x, screen_grid_y in grid_dimension(camera_pos, grid_size, window.size):
            pygame.draw.line(screen, color, (screen_grid_x, 0), (screen_grid_x, window_width))
            pygame.draw.line(screen, color, (0, screen_grid_y), (window_height, screen_grid_y))

        size = (window_width + grid_size, window_height + grid_size)
        for screen_grid_x, screen_grid_y in grid_dimension(camera_pos, grid_size, size):
            screen_grid_x -= grid_size
            screen_grid_y -= grid_size
            text = (
                f'{(screen_grid_x - camera_pos[0]) // grid_size}'
                f',{(screen_grid_y - camera_pos[1]) // grid_size}'
            )
            image = font.render(text, True, color)
            screen.blit(image, (screen_grid_x, screen_grid_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    dx, dy = event.rel
                    camera_pos[0] += dx
                    camera_pos[1] += dy
        pygame.display.flip()
        clock.tick(framerate)

def argument_parser():
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        '--grid-size',
        type = int,
        default = 100,
        help = 'Width and height of grid on screen.',
    )
    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)
    run(args.display_size, args.framerate, args.grid_size)

if __name__ == "__main__":
    main()
