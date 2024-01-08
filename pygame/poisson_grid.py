import math
import random
import pygame

def generate_poisson_points(lambda_parameter, width, height):
    # Function to generate points on a grid using Poisson distribution
    cell_size = 1.0 / lambda_parameter
    grid_width = math.ceil(width / cell_size)
    grid_height = math.ceil(height / cell_size)
    grid = [[False] * grid_width for _ in range(grid_height)]
    for i in range(100 * math.ceil(lambda_parameter)):
        # Generate more points than expected
        x, y = random.random() * width, random.random() * height
        # Use floor division to convert to integer
        grid_x, grid_y = int(x // cell_size), int(y // cell_size)
        if not grid[grid_y][grid_x]:
            yield (x, y)
            grid[grid_y][grid_x] = True

WIDTH, HEIGHT = 600, 400
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
    for point in points:
        pygame.draw.circle(screen, 'white', (round(point[0]), round(point[1])), 2)
    pygame.display.flip()
    clock.tick(FPS)
