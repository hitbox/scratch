import itertools as it
import math

import pygamelib

from pygamelib import pygame

def point_inside_polygon(x, y, polygon):
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def get_outside_points(rects):
    for rect1 in rects:
        for point in pygamelib.corners(rect1):
            other_rects = (rect2 for rect2 in rects if rect2 != rect1)
            if not any(rect2 for rect2 in other_rects if rect2.collidepoint(point)):
                yield point

def run(display_size, framerate, background, rects):
    clock = pygame.time.Clock()
    running = True
    dragging = None
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
                    for rect in rects:
                        if rect.collidepoint(event.pos):
                            dragging = rect
                            break
                    else:
                        dragging = None
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    dragging = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    dragging.topleft += pygame.Vector2(event.rel)
        points = [point for rect in rects for point in pygamelib.corners(rect)]
        n = len(points)
        xs, ys = zip(*points)
        cx = sum(xs) / n
        cy = sum(ys) / n

        def angle(p):
            x, y = p
            return math.atan2(y - cx, x - cy)

        outside_points = list(get_outside_points(rects))
        if not outside_points:
            ordered_points = []
        else:
            lines = [line for rect in rects for line in pygamelib.side_lines(rect)]
            for line1, line2 in it.combinations(lines, 2):
                point = pygamelib.line_line_intersection(line1, line2)
                if point:
                    outside_points.append(point)
            ordered_points = sorted(outside_points, key=angle)

        screen.fill(background)
        for rect in rects:
            pygame.draw.rect(screen, 'magenta', rect, 1)
        pygame.draw.circle(screen, 'purple', (cx, cy), 10)

        if ordered_points:
            pygame.draw.polygon(screen, 'white', ordered_points, 1)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    pygamelib.add_shapes_from_file_arguments(parser)
    args = parser.parse_args(argv)

    rects = list(map(pygame.Rect, pygamelib.shapes_from_args(args)))
    run(args.display_size, args.framerate, args.background, rects)

if __name__ == '__main__':
    main()
