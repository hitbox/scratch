import argparse
import functools as ft
import itertools as it
import math
import unittest

import pygamelib

from pygamelib import pygame

angles = list(map(math.radians, range(0, 360, 45)))

class TestModuloRange(unittest.TestCase):

    def test_modulo_indexes(self):
        expect = [0,1,2,0,1]
        result = list(modulorange(0,5,3))
        self.assertEqual(expect, result)


def modulorange(start, distance, length):
    """
    Go distance `distance` indexes from `start`-ing index over an indexable of
    length `length`.
    """
    _distance = 0
    while _distance < distance:
        yield start
        start = (start + 1) % length
        _distance += 1

def run(display_size, framerate):
    screen = pygame.display.set_mode(display_size)
    frame = screen.get_rect()
    clock = pygame.time.Clock()
    font = pygamelib.monospace_font(30)

    subject = frame.inflate((-2*min(frame.size)/3,)*2)

    color = 'darkslategrey'
    radius = min(subject.size) / 2

    draw_line = ft.partial(pygame.draw.line, screen, color)
    draw_arc = ft.partial(pygame.draw.arc, screen, color, subject)

    lines = (
        (
            draw_line,
            (
                frame.center,
                pygame.Vector2(frame.center) + pygame.Vector2(1, 0) * radius,
                10,
            ),
        )
        for angle in angles
    )
    arcs = ((draw_arc, angles + (10,)) for angles in it.combinations(angles, 2))
    draws = it.cycle(it.chain(lines, arcs))

    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        screen.fill('peru')
        drawfunc, *argslist = next(draws)
        for args in argslist:
            drawfunc(*args)
        text_lines = [
            f'{clock.get_fps():.2f}',
        ]
        images = [font.render(line, True, color) for line in text_lines]
        rects = [image.get_rect() for image in images]
        for r1, r2 in it.pairwise(rects):
            r2.topright = r1.bottomright
        wrapped = pygame.Rect(pygamelib.wrap(rects))
        positioned = wrapped.copy()
        positioned.bottomright = frame.bottomright
        delta = pygame.Vector2(positioned.topleft) - wrapped.topleft
        for rect in rects:
            rect.topleft += delta
        for image, rect in zip(images, rects):
            screen.blit(image, rect)
        pygame.display.update()

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args.display_size, args.framerate)

if __name__ == '__main__':
    main()

# 2023-11-27
# - https://quillette.com/2023/11/27/chasing-the-ice-moon/
# - https://cdn.quillette.com/2023/11/Screenshot-2023-11-24-at-6.32.33-AM.png
# - Thought the line and circle segments were cool and wanted to generate every
#   permutation.
