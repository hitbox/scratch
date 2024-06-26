import itertools as it
import math

import pygamelib

from pygamelib import pygame

def run(display_size, framerate, background, rects):
    rect1, rect2 = rects
    window = pygame.Rect((0,0), display_size)
    running = True
    dragging = None
    clock = pygame.time.Clock()
    font = pygamelib.monospace_font(20)
    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if rect1.collidepoint(event.pos):
                    dragging = rect1
                elif rect2.collidepoint(event.pos):
                    dragging = rect2
                else:
                    dragging = None
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0] and dragging:
                    dragging.topleft += pygame.Vector2(event.rel)
        screen.fill(background)

        pygame.draw.rect(screen, 'brown', rect1.clip(rect2), 0)

        # draw rects and labels
        for index, rect in enumerate(rects):
            pygame.draw.rect(screen, 'grey20', rect, 4)
            image = font.render(f'rect{index}', True, 'grey20')
            screen.blit(image, image.get_rect(center=rect.center))

        ## draw segment points
        #points = list(pygamelib.rect_rect_segments(rect1, rect2))
        #for index, p in enumerate(points):
        #    pygame.draw.circle(screen, 'red', p, 4)
        #    image = font.render(f'{index}', True, 'white')
        #    screen.blit(image, p)

        ## devel:
        #if not rect1.contains(rect2):
        #    for p1, p2 in pygamelib.walk_outline(rect1, rect2):
        #        pygame.draw.line(screen, 'magenta', p1, p2, 2)

        points = list(pygamelib.walk_outline_pointwise(rect1, rect2))
        if len(points) > 1:
            pygame.draw.lines(screen, 'yellow', False, points, 1)
        for index, point in enumerate(points):
            pygame.draw.circle(screen, 'red', point, 4)
            image = font.render(f'{index}', True, 'white')
            screen.blit(image, point)

        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'rects',
        nargs = 2,
        type = pygamelib.rect_type,
        help = 'Pair of rect arguments.',
    )
    args = parser.parse_args(argv)

    rects = list(map(pygame.Rect, args.rects))
    run(args.display_size, args.framerate, args.background, rects)

if __name__ == '__main__':
    main()

# NOTES
# - this gets the points we want
# - need to order them
