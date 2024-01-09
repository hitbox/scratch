import argparse
import contextlib
import math
import os
import random

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

def generate_poisson_points(lambda_parameter, width, height):
    # Function to generate points on a grid using Poisson distribution
    cell_size = 1.0 / lambda_parameter
    grid_width = math.ceil(width / cell_size)
    grid_height = math.ceil(height / cell_size)
    grid = set()
    for _ in range(100 * math.ceil(lambda_parameter)):
        # Generate more points than expected
        x = random.random() * width
        y = random.random() * height
        # Use floor division to convert to integer
        grid_x = int(x // cell_size)
        grid_y = int(y // cell_size)
        if (grid_x, grid_y) not in grid:
            grid.add((grid_x, grid_y))
            yield (x, y)

def run():
    WIDTH = 600
    HEIGHT = 400
    FPS = 60

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Adjust this value for point density
    lambda_parameter = 0.03
    points = list(generate_poisson_points(lambda_parameter, WIDTH, HEIGHT))

    running = True
    while running:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        for point in points:
            center = tuple(map(round, point))
            pygame.draw.circle(screen, 'white', center, 2)
        pygame.display.flip()
        clock.tick(FPS)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()
