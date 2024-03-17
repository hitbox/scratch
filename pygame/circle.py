import math

import pygamelib

from pygamelib import pygame

def circle_point(center, radius, angle):
    cx, cy = center
    x = cx + math.cos(angle) * radius
    y = cy + math.sin(angle) * radius
    return (x, y)

def angle_to(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

def outer_tangent_angles(center, radius, point):
    d = math.dist(center, point)
    if d < radius:
        return
    cx, cy = center
    px, py = point
    angle = angle_to(center, point)
    alpha = math.asin(radius / d)
    beta = math.tau / 4 - alpha
    yield angle - beta
    yield angle + beta

def run(display_size, framerate, background):
    variables = [
        'center_to_point_angle',
        'a1',
        'a2',
    ]
    font = pygamelib.monospace_font(20)
    printer = pygamelib.FontPrinter(font, 'linen')
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.set_mode(display_size)
    pygame.mouse.set_visible(False)
    point = pygame.mouse.get_pos()
    window = screen.get_rect()
    center = window.center
    radius = window.width // 12
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEMOTION:
                point = event.pos
        # update
        center_to_point_angle = angle_to(center, point)
        # draw
        screen.fill(background)
        distance = math.dist(center, point)
        if distance >= radius:
            angles = outer_tangent_angles(center, radius, point)
            a1, a2 = angles

            p1 = circle_point(center, radius, a1)
            p2 = circle_point(center, radius, a2)
            pygame.draw.circle(screen, 'red', p1, 6)
            pygame.draw.circle(screen, 'green', p2, 6)

            points = [point]

            def gen(n):
                mixfunc = pygamelib.mixangle_longest
                for i in range(n+1):
                    yield mixfunc(a2, a1, i / n)

            n = 10
            points.extend(circle_point(center, radius, angle) for angle in gen(n))

            if len(points) > 2:
                pygame.draw.polygon(screen, 'brown', points, 4)
                for index, p in enumerate(points):
                    image = font.render(f'{index}', True, 'linen')
                    screen.blit(image, p)

        # point at cursor
        pygame.draw.circle(screen, 'yellow', point, 3)
        pygame.draw.line(screen, 'grey20', (center[0], window.top), (center[0], window.bottom))
        pygame.draw.line(screen, 'grey20', (0, center[1]), (window.right, center[1]))
        # the circle
        pygame.draw.circle(screen, 'grey20', center, radius, 1)
        px = center[0] + math.cos(center_to_point_angle) * radius
        py = center[1] + math.sin(center_to_point_angle) * radius
        calculated_point_on_circle = (px, py)
        pygame.draw.line(screen, 'darkslateblue', center, calculated_point_on_circle)
        # print variables
        lines = ((key, val) for key, val in locals().items() if key in variables)
        lines = sorted(lines, key=lambda item: variables.index(item[0]))
        lines = [f'{key}={val}' for key, val in lines]
        if lines:
            image = printer(lines)
            screen.blit(image, (0,0))
        pygame.display.flip()
        clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args.display_size, args.framerate, args.background)

if __name__ == '__main__':
    main()
