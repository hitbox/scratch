import itertools as it
import math

import pygamelib

from pygamelib import pygame

corners_funcs = {
    True: pygamelib.ccw_corners_with_point,
    False: pygamelib.corners_with_point,
}

def run(display_size, framerate, background, rects, ccw=False):
    rects = tuple(map(pygame.Rect, rects))
    rect1, rect2 = rects
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
        if rect1.colliderect(rect2):
            points = list(pygamelib.outline_rects(*rects))
            if points:
                pygame.draw.polygon(screen, 'brown', points, 1)
                for index, point in enumerate(points):
                    pygame.draw.circle(screen, 'brown', point, 4)
                    image = font.render(f'{index}', True, 'white')
                    screen.blit(image, image.get_rect(center=point))
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'rects',
        nargs = 2,
        type = pygamelib.rect_type,
    )
    parser.add_argument(
        '--ccw',
        action = 'store_true',
    )
    args = parser.parse_args(argv)
    run(args.display_size, args.framerate, args.background, args.rects, args.ccw)

if __name__ == '__main__':
    main()

# 2024-04-03 Wed.
# - want demo that cw and ccw looping around rects works
