import argparse
import contextlib
import functools as ft
import itertools as it
import math
import os
import random
import textwrap
import unittest

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

angles = (0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330)
angles = (0, 45, 90, 180, 270)
angles = list(map(math.radians, angles))

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

def wraprects(rects):
    return pygame.Rect((0,)*4).unionall(rects)

def copyrect(rect, **kwargs):
    rect = rect.copy()
    for key, val in kwargs.items():
        setattr(rect, key, val)
    return rect

def run():
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    frame = screen.get_rect()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('monospace', 30)
    framerate = 60

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
    from pprint import pprint

    frame_number = 0
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
        for r1, r2 in zip(rects, rects[1:]):
            r2.topright = r1.bottomright
        wrapped = pygame.Rect((0,)*4).unionall(rects)
        positioned = wrapped.copy()
        positioned.bottomright = frame.bottomright
        delta = pygame.Vector2(positioned.topleft) - wrapped.topleft
        for rect in rects:
            rect.topleft += delta
        for image, rect in zip(images, rects):
            screen.blit(image, rect)
        pygame.display.update()
        frame_number += 1

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()

# 2023-11-27
# - https://quillette.com/2023/11/27/chasing-the-ice-moon/
# - https://cdn.quillette.com/2023/11/Screenshot-2023-11-24-at-6.32.33-AM.png
# - Thought the line and circle segments were cool and wanted to generate every
#   permutation.
