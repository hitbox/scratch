import pygamelib

from pygamelib import pygame

def wrap_points(points):
    xs, ys = zip(*points)

    left = min(xs)
    top = min(ys)
    right = max(xs)
    bottom = max(ys)

    return (left, top, right - left, bottom - top)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)

    window = pygame.Rect((0,0), args.display_size)

    letter_a_color = 'azure'
    letter_a_shape = [
        dict(
            func = pygame.draw.lines,
            color = letter_a_color,
            closed = True,
            points = [
                (-1, -10), # top, left side
                (-8, +10), # left leg, left side
                (-5, +10), # left leg, right side
                (-3, +5), # center cross, left
                (+3, +5), # center cross, right
                (+5, +10), # right left, left side
                (+8, +10), # right left, left side
                (+1, -10), # top, right side
            ],
        ),
        dict(
            func = pygame.draw.lines,
            color = letter_a_color,
            closed = True,
            points = [
                (+0, -5),
                (-3, +3),
                (+3, +3),
            ],
        ),
    ]

    all_points = []
    letter_a_scale = 20
    for subshape in letter_a_shape:
        points = subshape['points']
        all_points.extend(points)
        for index, point in enumerate(points):
            points[index] = tuple(x * letter_a_scale for x in point)

    boundary = pygame.Rect(wrap_points(all_points))
    aligned = boundary.copy()
    aligned.center = window.center

    dx, dy = pygame.Vector2(boundary.topleft) - aligned.topleft
    for subshape in letter_a_shape:
        points = subshape['points']
        for index, (x, y) in enumerate(points):
            points[index] = (x - dx, y - dy)

    clock = pygame.time.Clock()
    gui_font = pygamelib.monospace_font(30)
    printer = pygamelib.FontPrinter(gui_font, 'azure')
    screen = pygame.display.set_mode(window.size)

    time = 0.0
    time_delta = 0.0005
    elapsed = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()

        screen.fill('black')
        # XXX
        # - Hey, okay, this works pretty good to trace the lines.
        # - Wanted to "draw" the lines over time.
        # - Need to accumulate the lines we've travelled.
        # - See pygamelib.segmented_lerp.
        for subshape in letter_a_shape:
            func = subshape['func']
            color = subshape['color']
            closed = subshape['closed']
            points = subshape['points']
            func(screen, color, closed, points)

            p = pygamelib.segmented_lerp(points, time, closed=True)
            pygame.draw.circle(screen, 'crimson', p, 5)

        # Debugging.
        lines = [
            f'FPS: {clock.get_fps():.0f}',
        ]
        image = printer(lines)
        screen.blit(image, (0,0))
        pygame.display.flip()
        elapsed = clock.tick()
        if time + time_delta > 1:
            time = 0
        else:
            time += time_delta

if __name__ == '__main__':
    main()
