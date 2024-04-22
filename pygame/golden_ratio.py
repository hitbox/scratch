import itertools as it
import math

import pygamelib

from pygamelib import pygame

alignments = it.cycle(['topleft', 'topright', 'bottomright', 'bottomleft'])

phi = (1 + math.sqrt(5)) / 2

def golden_rect(inside):
    """
    Continuously generate golden ratio rects inside the `inside` rect. After
    yielding, the golden rect becomes the new `inside`.
    """
    while True:
        minside = min(inside.size)
        maxside = max(inside.size)
        square = pygame.Rect((0,)*2, (minside,)*2)
        attr = next(alignments)
        setattr(square, attr, getattr(inside, attr))
        yield square

        if inside.width > inside.height:
            # horizontal
            _inside = pygame.Rect(0, inside.top, maxside - minside, inside.height)
            if 'left' in attr:
                _inside.right = inside.right
            else:
                _inside.left = inside.left
        else:
            # vertical
            _inside = pygame.Rect(inside.left, 0, inside.width, maxside - minside)
            if 'top' in attr:
                _inside.bottom = inside.bottom
            else:
                _inside.top = inside.top

        inside = _inside

def scale_rects_as_points(rects, center, delta_radius):
    for rect in rects:
        newrect_corners = []
        for point in pygamelib.corners(rect):
            angle = math.atan2(point[1] - center[1], point[0] - center[0])
            radius = math.dist(point, center) + delta_radius
            _point = (
                center[0] + math.cos(angle) * radius,
                center[1] + math.sin(angle) * radius,
            )
            newrect_corners.append(_point)
        newrect = pygamelib.rect_from_points(newrect_corners)
        yield newrect

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)

    display_size = args.display_size
    framerate = args.framerate
    background = args.background

    window = pygamelib.make_rect(size=display_size)

    rect = window.inflate(-100, -100)
    rect.height /= phi
    rect.center = window.center

    goldens = golden_rect(rect)
    saved = [rect.copy()]
    golden = next(goldens)
    scale_delta = 5

    elapsed = 0
    running = True
    font = pygamelib.monospace_font(20)
    font_printer = pygamelib.FontPrinter(font, 'azure')
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    saved.append(golden)
                    golden = next(goldens)
                elif event.button in (pygame.BUTTON_WHEELUP, pygame.BUTTON_WHEELDOWN):
                    if event.button == pygame.BUTTON_WHEELDOWN:
                        delta = -scale_delta
                    elif event.button == pygame.BUTTON_WHEELUP:
                        delta = +scale_delta
                    saved = list(scale_rects_as_points(saved, window.center, delta))
                    golden = next(scale_rects_as_points([golden], window.center, delta))

        screen.fill(background)
        image = font_printer([
            'Escape or Q to quit',
            'Other key to generate new gold rect',
        ])
        screen.blit(image, (0,0))
        for _rect in saved:
            pygame.draw.rect(screen, 'grey20', _rect, 1)
        pygame.draw.rect(screen, 'gold', golden, 1)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

if __name__ == '__main__':
    main()
