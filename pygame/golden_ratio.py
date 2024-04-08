import itertools as it
import math

import pygamelib

from pygamelib import pygame

alignments = it.cycle(['topleft', 'topright', 'bottomright', 'bottomleft'])

def golden_rect(inside):
    minside = min(inside.size)
    maxside = max(inside.size)
    square = pygame.Rect((0,)*2, (minside,)*2)
    attr = next(alignments)
    print(f'{attr=}')
    setattr(square, attr, getattr(inside, attr))

    is_vert = inside.height > inside.width
    print(f'{inside=}')
    print(f'{square=}')
    print(f'{is_vert=}')
    yield square

    sidediff = maxside - minside

    if is_vert:
        # square was aligned inside a vertical rect
        # next will be horizontal
        width = sidediff
        height = inside.height
    else:
        width = inside.width
        height = sidediff

    if attr == 'bottomleft':
        x, y = square.topright
    elif attr == 'topright':
        x, y = square.bottomleft
    elif attr == 'bottomright':
        x, y = inside.topleft
    elif attr == 'topleft':
        x, y = square.topleft

    _inside = pygame.Rect(x, y, width, height)
    yield from golden_rect(_inside)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'rect',
        type = pygamelib.rect_type(with_pygame=True),
    )
    args = parser.parse_args(argv)

    display_size = args.display_size
    framerate = args.framerate
    background = args.background
    rect = args.rect

    goldens = golden_rect(rect)
    saved = []
    golden = next(goldens)

    window = pygamelib.make_rect(size=display_size)
    elapsed = 0
    running = True
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(window.size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
                else:
                    saved.append(golden)
                    golden = next(goldens)
        screen.fill(background)
        pygame.draw.rect(screen, 'grey20', rect, 1)
        for _rect in saved:
            pygame.draw.rect(screen, 'grey20', _rect, 1)
        pygame.draw.rect(screen, 'gold', golden, 1)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

if __name__ == '__main__':
    main()
