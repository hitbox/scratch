import itertools as it
import math

import polylib
import pygamelib

from pygamelib import pygame

corners_funcs = {
    True: pygamelib.ccw_corners_with_point,
    False: pygamelib.corners_with_point,
}

def rect2poly(rect):
    return list(pygamelib.corners(rect))

def run(
    display_size,
    framerate,
    background,
    rect1,
    rect2,
    ccw = False,
):
    window = pygame.Rect((0,0), display_size)
    running = True
    dragging = None
    clock = pygame.time.Clock()
    font = pygamelib.monospace_font(30)
    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if rect2.collidepoint(event.pos):
                        dragging = rect2
                    else:
                        dragging = None
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    dragging = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    dragging.topleft += pygame.Vector2(event.rel)
        screen.fill(background)
        pygame.draw.rect(screen, 'grey10', rect1, 4)
        pygame.draw.rect(screen, 'grey50', rect2, 1)
        poly1, poly2 = map(rect2poly, [rect1, rect2])
        clipped = polylib.clip(poly1, poly2)
        if len(clipped) > 1:
            pygame.draw.polygon(screen, 'grey90', clipped, 1)
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
    parser.add_argument(
        '--ccw',
        action = 'store_true',
    )
    args = parser.parse_args(argv)
    run(
        args.display_size,
        args.framerate,
        args.background,
        args.rect1,
        args.rect2,
        args.ccw
    )

if __name__ == '__main__':
    main()

# 2024-04-03 Wed.
# - want demo that cw and ccw looping around rects works
