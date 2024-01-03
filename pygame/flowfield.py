import argparse
import contextlib
import math
import os
import random

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

WIDTH = 600
HEIGHT = 400
CELL_SIZE = 20
ROWS = HEIGHT // CELL_SIZE
COLS = WIDTH // CELL_SIZE

def vector_grid(rows, cols):
    grid = [
        [
            pygame.Vector2(
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            ).normalize()
            for _ in range(cols)
        ]
        for _ in range(rows)
    ]
    return grid

def run():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    framerate = 60

    # grid of vectors
    vectors = vector_grid(ROWS, COLS)

    running = True
    while running:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        for y in range(ROWS):
            for x in range(COLS):
                start_pos = (
                    x * CELL_SIZE + CELL_SIZE // 2,
                    y * CELL_SIZE + CELL_SIZE // 2
                )
                end_pos = (
                    start_pos[0] + vectors[y][x][0] * CELL_SIZE // 2,
                    start_pos[1] + vectors[y][x][1] * CELL_SIZE // 2
                )
                pygame.draw.line(screen, 'white', start_pos, end_pos, 1)
        pygame.draw.circle(screen, 'red', (int(WIDTH/2), int(HEIGHT/2)), 5)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()

# 2024-01-03
# - https://damoonrashidi.me/articles/flow-field-methods
# - asked chatgpt to generate something
# - cleaned it up

