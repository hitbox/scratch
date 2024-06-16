import math

import pygamelib

from pygamelib import pygame

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)

    window = pygame.Rect((0,0), args.display_size)

    control_point_radius = 10
    control_points = list(map(pygame.Vector2, pygamelib.corners(
        window.inflate(-window.width//2, -window.height//2))))
    midpoints = [
        pygame.Vector2(
            pygamelib.midpoint(
                control_points[i],
                control_points[(i+1)%len(control_points)]
            )
        )
        for i in range(len(control_points))
    ]
    hovering = None
    dragging = None

    moved = False
    screen = pygame.display.set_mode(window.size)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
            elif event.type == pygame.MOUSEMOTION:
                if not any(event.buttons):
                    # no buttons check hovering
                    for control_point in control_points:
                        if control_point.distance_to(event.pos) < control_point_radius:
                            hovering = control_point
                            break
                    else:
                        hovering = None
                elif event.buttons[0] and dragging:
                    # moving mouse with left mouse button
                    dragging += event.rel
                    moved = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    # released left mouse button, no hovering
                    hovering = None
                    dragging = None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                # TODO
                # - right click to drag canvas
                # clicked left mouse button
                if hovering:
                    dragging = hovering
                    hovering = None
        # update midpoints
        if moved:
            for index, midpoint in enumerate(midpoints):
                p1 = control_points[index]
                p2 = control_points[(index + 1) % len(control_points)]
                midpoint.update(pygamelib.midpoint(p1, p2))
            moved = False

        screen.fill('black')
        pygame.draw.lines(screen, 'gold', True, control_points)
        for point in control_points:
            if point is hovering:
                width = 0
            else:
                width = 1
            pygame.draw.circle(screen, 'brown', point, control_point_radius, width)
        pygame.draw.lines(screen, 'purple', True, midpoints)
        pygame.display.flip()

if __name__ == '__main__':
    main()
