import argparse

import pygamelib

from pygamelib import pygame

def main(argv=None):
    parser = pygamelib.command_line_parser(
        description = 'Demo simplest possible dragging with pygame.',
    )
    args = parser.parse_args(argv)

    screen = pygame.display.set_mode(args.display_size)
    rect = screen.get_rect().inflate((-600,)*2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0] and rect.collidepoint(event.pos):
                    rect.topleft += pygame.Vector2(event.rel)
        screen.fill('black')
        pygame.draw.rect(screen, 'orange', rect, 0)
        pygame.display.flip()

if __name__ == '__main__':
    main()

# 2024-03-04 Mon.
# - trying to think of the simplest possible way to drag
# - this works but also "pushes" the rect
# - maybe maintain a collection of draggables and which ones were initially
#   clicked and only those are considered dragging
# - other problem is you can drag too fast and lose the dragging
# 2024-03-11 Mon.
# - added main func
# - silence pygame with pygamelib
# - use pygamelib more
