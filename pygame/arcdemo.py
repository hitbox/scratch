import math

import pygamelib

from pygamelib import pygame

def ellipse_points(center, size, npoints, angle1=None, angle2=None):
    if angle1 is None:
        angle1 = 0
    if angle2 is None:
        angle2 = math.tau
    cx, cy = center
    width, height = size
    rx = width / 2
    ry = height / 2
    j = npoints - 1
    for i in range(npoints):
        angle = angle1 + (angle2 - angle1) * i / j
        x = cx + rx * math.cos(angle)
        y = cy + ry * -math.sin(angle)
        yield (x, y)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'rect',
        type = pygamelib.rect_type(with_pygame=True),
    )
    parser.add_argument(
        'angle1',
        type = int,
    )
    parser.add_argument(
        'angle2',
        type = int,
    )
    parser.add_argument(
        '--npoints',
        default = 30,
        type = int,
    )
    args = parser.parse_args(argv)

    display_size = args.display_size
    framerate = args.framerate
    background = args.background
    rect = args.rect
    angle1 = math.radians(args.angle1)
    angle2 = math.radians(args.angle2)
    npoints = args.npoints

    polygon = list(ellipse_points(rect.center, rect.size, npoints, angle1, angle2))

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
        screen.fill(background)
        pygame.draw.rect(screen, 'grey20', rect, 1)
        pygame.draw.line(screen, 'grey20', rect.midtop, rect.midbottom, 1)
        pygame.draw.line(screen, 'grey20', rect.midleft, rect.midright, 1)
        #pygame.draw.arc(screen, 'white', rect, math.radians(angle1), math.radians(angle2), 1)
        pygame.draw.lines(screen, 'brown', False, polygon, 1)

        pygame.display.flip()
        elapsed = clock.tick(framerate)

if __name__ == '__main__':
    main()
