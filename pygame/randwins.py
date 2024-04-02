import itertools as it
import random

import pygamelib

from pygamelib import pygame

class Window:

    def __init__(self, rect, offset=None, points=None):
        self.rect = rect
        if offset is None:
            offset = (0, 0)
        self.offset = pygame.Vector2(offset)
        if points is None:
            points = []
        self.points = points


def run(display_size, framerate, background, windows):
    window = pygame.Rect((0,0), display_size)

    active_index = 0
    active_window = windows[active_index]
    running = True
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
                elif event.key == pygame.K_TAB:
                    active_index = (active_index + 1) % len(windows)
                    active_window = windows[active_index]
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    active_window.offset += event.rel
        screen.fill(background)
        # NOTES
        # - captures random points into random windows correctly
        # - renders correctly
        # - drag to move active window offset
        # TODO
        # - separate concerns
        # - minimize main loop
        # - window title bar to drag window itself
        # - should points move with window?
        for window in windows:
            if window is active_window:
                color = 'white'
                pygame.draw.rect(screen, color, window.rect, 1)
            else:
                if active_window.rect.contains(window.rect):
                    # behind active window, completely invisible
                    continue
                else:
                    color = 'grey20'
                    pygame.draw.rect(screen, color, window.rect, 1)
            pressed = pygame.key.get_pressed()
            dx = -pressed[pygame.K_LEFT] + pressed[pygame.K_RIGHT]
            dy = -pressed[pygame.K_UP] + pressed[pygame.K_DOWN]
            active_window.rect.topleft += pygame.Vector2(dx, dy)

            wx, wy = window.rect.topleft
            for point in window.points:
                px, py = point
                screen_point = window.offset + (wx + px, wy + py)
                if window.rect.collidepoint(screen_point):
                    if window is not active_window:
                        if active_window.rect.collidepoint(screen_point):
                            continue
                    pygame.draw.circle(screen, 'red', screen_point, 4)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    pygamelib.add_seed_option(parser)
    pygamelib.add_number_option(
        parser,
        name = '--npoints',
        help = 'Number of random points. Default: %(default)s.',
    )
    pygamelib.add_number_option(
        parser,
        name = '--nwindows',
        help = 'Number of random windows. Default: %(default)s.',
    )
    args = parser.parse_args(argv)

    if args.seed:
        random.seed(args.seed)

    if args.nwindows > args.npoints:
        parser.error('more windows than points')
        return

    domain = pygame.Rect((0,0), args.display_size)

    points = [pygamelib.random_point(domain) for _ in range(args.npoints)]
    window_rects = [
        pygamelib.random_rect2(domain, minsize=(100, 100))
        for _ in range(args.nwindows)
    ]

    points_per_window = args.npoints // args.nwindows

    windows = []
    while window_rects:
        window_rect = pygame.Rect(window_rects.pop())
        window = Window(window_rect)
        windows.append(window)
        wx, wy, _, _ = window_rect
        for _ in range(points_per_window):
            px, py = points.pop()
            window.points.append((px - wx, py - wy))

    run(args.display_size, args.framerate, args.background, windows)

if __name__ == '__main__':
    main()

# 2024-04-01 Mon.
# - capture random points into random windows
# - scrollable windows to see all points
# - indicators of off-window points
