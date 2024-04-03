import itertools as it
import math

import pygamelib

from pygamelib import pygame

def run(display_size, framerate, background, rect, ccw=False):
    window = pygame.Rect((0,0), display_size)
    running = True
    nearest = None
    corners_funcs = {
        True: pygamelib.ccw_corners_with_point,
        False: pygamelib.corners_with_point,
    }
    corners = corners_funcs[ccw]
    clock = pygame.time.Clock()
    large_font = pygamelib.monospace_font(30)
    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
                elif event.key == pygame.K_TAB:
                    ccw = not ccw
                    corners = corners_funcs[ccw]
            elif event.type == pygame.MOUSEMOTION:
                nearest = pygamelib.nearest_point_on_rect(event.pos, rect)
        screen.fill(background)
        pygame.draw.rect(screen, 'brown', rect, 1)
        if nearest:
            pygame.draw.circle(screen, 'red', nearest, 4)
            points = corners(rect, nearest)
            for index, point in enumerate(points):
                image = large_font.render(f'{index}', True, 'white')
                screen.blit(image, image.get_rect(center=point))
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'rect',
        type = pygamelib.rect_type,
    )
    parser.add_argument(
        '--ccw',
        action = 'store_true',
    )
    args = parser.parse_args(argv)
    run(args.display_size, args.framerate, args.background, args.rect, args.ccw)

if __name__ == '__main__':
    main()

# 2024-04-03 Wed.
# - want demo that cw and ccw looping around rects works
