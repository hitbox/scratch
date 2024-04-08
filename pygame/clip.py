import itertools as it
import math

import pygamelib

from pygamelib import pygame

def run(display_size, framerate, background, rect1, rect2):
    window = pygame.Rect((0,0), display_size)
    running = True
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill(background)
        pygame.draw.rect(screen, 'grey20', rect1, 1)
        pygame.draw.rect(screen, 'grey20', rect2, 1)
        pygame.draw.rect(screen, 'red', rect1.clip(rect2), 0)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'rect1',
        type = pygamelib.rect_type(with_pygame=True),
    )
    parser.add_argument(
        'rect2',
        type = pygamelib.rect_type(with_pygame=True),
    )
    args = parser.parse_args(argv)

    run(args.display_size, args.framerate, args.background, args.rect1, args.rect2)

if __name__ == '__main__':
    main()
