import argparse
import itertools as it
import operator as op

import pygamelib

from pygamelib import pygame

def step(num, den):
    max_grid_side = max(num, den)
    # largest square side that fits inside the grid formed by num x den
    square_side = min(num, den)
    # number of square that fit inside this grid
    n_squares = max_grid_side // square_side
    total_square_side = square_side * n_squares
    remaining_max = max_grid_side - total_square_side
    return (remaining_max, square_side)

def division_algorithm(num, den):
    while num > 1 and den > 1:
        num, den = step(num, den)
        yield (num, den)

# take in chunks of squares
# groupby squares

# so if you had a grid of columns and rows: 17x10

# 17 is the thing to take squares from
# 10 is the ...don't know

# product(width, height) just happens to give us sorted in columns, such that
# if we take 10 chunks of 10 (this "other" axis), we have a square.

def wrap(rects):
    xs, ys, _, _ = zip(*rects)
    left = min(xs)
    right = max(xs)
    top = min(ys)
    bottom = max(ys)
    width = right - left
    height = bottom - top
    return (left, top, width, height)

def update_rect(rect, **kwargs):
    for key, val in kwargs.items():
        setattr(rect, key, val)

def unit_square_rect(side, i, j):
    x = i * side
    y = j * side
    rect = pygame.Rect(x, y, side, side)
    return rect

def unit_square_rects(side, width, height):
    # produces a mapping between index and position
    # width, height produces column-wise, such that taking chunks of the height
    # is a single column
    # height, width would rotate
    for i, j in it.product(*map(range, (width, height))):
        yield unit_square_rect(side, i, j)

def main_loop(num, den, rects, colors, borders, window):
    clock = pygame.time.Clock()
    pygame.font.init()
    font = pygame.font.SysFont(None, 28)
    screen = pygame.display.set_mode(window.size)
    running = True
    limit = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill('black')
        for index, (rect, color, border) in enumerate(zip(rects, colors, borders)):
            if index == limit:
                limit = (limit + 1) % len(rects)
                break
            pygame.draw.rect(screen, color, rect, border)
            col, row = divmod(index, den)
            text = f'{col},{row}'
            image = font.render(text, True, 'azure')
            screen.blit(image, image.get_rect(center=rect.center))
        pygame.display.flip()
        clock.tick(60)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('numerator', type=int)
    parser.add_argument('denominator', type=int)
    parser.add_argument('--unit-square', type=int, default=30)
    args = parser.parse_args(argv)

    num = args.numerator
    den = args.denominator
    unit_square = args.unit_square

    if num < den:
        parser.error('numerator must be greater than denominator.')

    ratios = list(division_algorithm(num, den))

    # going from top to bottom, rightward
    rects = list(unit_square_rects(unit_square, num, den))
    colors = ['grey10' for i, _ in enumerate(rects)]
    borders = [1 for _ in rects]

    window = pygame.Rect(0, 0, 1500, 900)

    # TODO
    # - left off around here
    # - centering the rects looks off by one unit square row and column
    # - can color the first square division but it is hard coded below
    # - how to take slices or remaining unit squares in grid, a subgrid, and
    #   fill it taking into account which way the squares are filling?

    # Yo! Working on blademode.py, I'm probably wrapping rects wrong here. Need
    # to get the rights and bottoms of the rects. Had a sudden thought that I'm
    # probably only getting the xy's.

    wrapped = pygame.Rect(wrap(rects))
    centered = wrapped.copy()
    #update_rect(centered, center=window.center)
    centered.center = window.center
    delta = pygame.Vector2(centered.topleft) - wrapped.topleft
    for rect in rects:
        rect.topleft += delta

    index_offset = 0

    # update color for first 10x10 unit rects horizontally
    for index, rect in enumerate(rects):
        if index_offset + index < 10 * 10:
            colors[index] = 'darkblue'

    main_loop(num, den, rects, colors, borders, window)

if __name__ == '__main__':
    main()

# 2024-06-05 Wed.
# MindYourDecisions
# "Can you solve this fraction question from China?"
# Visual Division Algorithm
# https://youtu.be/DFhf4KPiAXI?t=588
