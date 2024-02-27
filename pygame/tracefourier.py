import argparse
import itertools as it
import math

import pygamelib

from pygamelib import pygame

def coeffs(points, N):
    # Compute Fourier coefficients
    # TODO
    # - what is going on here?
    for n in range(N):
        a = sum(math.cos(math.tau * n * k / N) * p[0] for k, p in enumerate(points)) / N
        b = sum(math.sin(math.tau * n * k / N) * p[1] for k, p in enumerate(points)) / N
        yield (a, b)

def somecalc(a, b, n, t, somen, N):
    # TODO
    # - what is going on here?
    angle = math.tau * n * t / (somen * N)
    cosval = math.cos(angle)
    sinval = math.sin(angle)
    yield a * cosval - b * sinval
    yield a * sinval + b * cosval

def generate_points(points, N, somen):
    # Generate points using Fourier series
    for t in range(somen * N):
        x = 0
        y = 0
        for n, (a, b) in enumerate(coeffs(points, N)):
            dx, dy = somecalc(a, b, n, t, somen, N)
            x += dx
            y += dy
        yield (int(x), int(y))

def run(display_size, points, somen):
    screen = pygame.display.set_mode(display_size)

    N = len(points)
    gpoints = list(generate_points(points, N, somen))
    pygame.draw.lines(screen, 'red', False, gpoints, 1)
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('somen', type=int)
    pygamelib.add_point_arguments(parser, 'points')
    args = parser.parse_args(argv)
    run(args.display_size, args.points, args.somen)

if __name__ == '__main__':
    main()

# 2024-02-27 Tue.
# - https://injuly.in/blog/fourier-series/index.html
# - want to draw with fourier series
