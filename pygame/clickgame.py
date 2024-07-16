import math
import random

import pygamelib

from pygamelib import pygame

from animate2 import bezier

def ease_in(t):
    p0 = (0.0, 0.0)
    p1 = (0.25, 0.25)
    p2 = (0.5, 1.0)
    p3 = (1.0, 1.0)
    x, y = bezier(t, p0, p1, p2, p3)
    return y

class TimedCircle:

    def __init__(self, position, radius, lifespan):
        self.position = position
        self.radius = radius
        self.lifespan = lifespan
        self._lifespan = lifespan
        # TODO
        # - how to delay starting so that multiple can be spawned and be human
        #   clickable

    def collide_circle(self, other):
        d = self.position.distance_to(other.position)
        return d <= self.radius + other.radius

    def collide_point(self, position):
        d = self.position.distance_to(position)
        return d <= self.radius

    @property
    def is_alive(self):
        return self._lifespan > 0

    def update(self, elapsed):
        self._lifespan -= elapsed


def random_position(lifespan, radius, inside, existing):
    while True:
        x = random.randint(inside.left, inside.right)
        y = random.randint(inside.top, inside.bottom)
        position = pygame.Vector2(x, y)
        circle = TimedCircle(position, radius, lifespan)
        for other in existing:
            if circle.collide_circle(other):
                break
        else:
            return circle

def process_click(event, circles, success, offbeats, misses, rythm_tolerance):
    for circle in circles:
        if (
            circle.is_alive
            and
            circle.collide_point(event.pos)
        ):
            # clicked an alive circle
            if 0 < abs(circle._lifespan) < rythm_tolerance:
                # clicked within milliseconds of zero
                success.append(circle)
                break
            else:
                offbeats.append(circle)
    else:
        misses.append(event.pos)
    for other in success:
        if other in circles:
            circles.remove(other)

def run(args):
    font = pygamelib.monospace_font(20)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    spawn = window.inflate(-200, -200)
    circles = []
    success = []
    failed = []
    misses = []
    offbeats = []
    # FIXME
    # - messy complicated, duplicated code
    # - click "on time" instead of before timeout
    # - spawn circles in patterns, start with straight lines
    rythm_tolerance = 300

    spawn_radius = 100
    _spawn_radius = spawn_radius
    spawn_radius_step = 10
    spawn_radius_minimum = 30

    spawn_lifespan = 2_000
    _spawn_lifespan = spawn_lifespan
    spawn_lifespan_step = 100
    spawn_lifespan_minimum = 1000

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                process_click(event, circles, success, offbeats, misses, rythm_tolerance)
        screen.fill('black')
        for position in misses:
            pygame.draw.circle(screen, 'indigo', position, 10, 0)
        for circle in failed:
            pygame.draw.circle(screen, 'brown', circle.position, circle.radius, 1)
        for circle in success:
            pygame.draw.circle(screen, 'green4', circle.position, circle.radius, 1)
        for circle in circles:
            pygame.draw.circle(screen, 'azure', circle.position, circle.radius, 2)
            # draw rythm circle
            lifespan_t = ease_in(circle._lifespan / circle.lifespan)
            lifespan_radius = pygamelib.mix(
                lifespan_t,
                circle.radius,
                circle.radius * 3,
            )
            lifespan_width = int(pygamelib.mix(lifespan_t, 1, circle.radius))
            if circle in offbeats:
                color = 'yellow'
            else:
                color = 'azure'
            pygame.draw.circle(screen, color, circle.position, lifespan_radius, lifespan_width)
            image = font.render(f'{circle._lifespan}', True, color)
            screen.blit(image, image.get_rect(center=circle.position))
        pygame.display.flip()
        elapsed = clock.tick()
        for circle in circles:
            circle.update(elapsed)
            if not circle.is_alive:
                failed.append(circle)
        for circle in failed:
            if circle in circles:
                circles.remove(circle)
        if not circles:
            for lifespan_offset in range(0, _spawn_lifespan*3, _spawn_lifespan):
                lifespan = _spawn_lifespan + lifespan_offset
                circle = random_position(lifespan, _spawn_radius, spawn, circles)
                circles.append(circle)
            if _spawn_lifespan - spawn_lifespan_step >= spawn_lifespan_minimum:
                _spawn_lifespan -= spawn_lifespan_step
            if _spawn_radius - spawn_radius_step >= spawn_radius_minimum:
                _spawn_radius -= spawn_radius_step

def argument_parser():
    parser = pygamelib.command_line_parser()
    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)
    run(args)

if __name__ == '__main__':
    main()

# 2024-07-16 Tue.
# - Never hear of this game Osu
# - https://www.youtube.com/watch?v=s6nOCzBVSJE
# - Wanted to make a simpler version where you just click random, timed
#   circles.
