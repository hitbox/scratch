import argparse
import itertools as it
import math
import random
import random

import pygamelib

from pygamelib import pygame

grad3 = [
    [1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0],
    [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1],
    [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1],
]

F2 = 0.5 * (math.sqrt(3.0) - 1.0)
G2 = (3.0 - math.sqrt(3.0)) / 6.0

def fade(t):
    """
    Fade function for smoothing interpolation weights.

    Parameters:
        t (float): Input value to be faded.

    Returns:
        float: Smoothed value based on the input.
    """
    # The fade function is used to smooth out the interpolation
    # It creates a smoother transition between gradient vectors
    # by using a quintic polynomial
    # The formula t * t * t * (t * (t * 6 - 15) + 10)
    # produces this smoothing effect
    return t * t * t * (t * (t * 6 - 15) + 10)

def lerp(a, b, t):
    """
    Linear interpolation between two values.

    Parameters:
        a (float): Start value.
        b (float): End value.
        t (float): Interpolation factor.

    Returns:
        float: Interpolated value between a and b.
    """
    # Linear interpolation formula:
    # lerp(a, b, t) = a + t * (b - a)
    # This function interpolates between a and b based on the value of t
    return a + t * (b - a)

def gradient(h, x, y):
    """
    Calculate the dot product between a random gradient vector and a distance vector.

    Parameters:
        h (int): Hash value for choosing the gradient vector.
        x (float): X-coordinate of the distance vector.
        y (float): Y-coordinate of the distance vector.

    Returns:
        float: Dot product of the gradient and distance vectors.
    """
    # 2D vectors
    vectors = [
        [1, 1], [-1, 1], [1, -1], [-1, -1],
        [1, 0], [-1, 0], [0, 1], [0, -1]
    ]
    # Choose a gradient vector based on the hash value
    idx = h & 7
    g = vectors[idx]
    # Dot product of gradient and distance vector
    return g[0] * x + g[1] * y

def perlin_noise(width, height, scale):
    """
    Generate Perlin noise.

    Parameters:
        width (int): Width of the noise grid.
        height (int): Height of the noise grid.
        scale (float): Scale factor controlling the frequency of the noise.

    Returns:
        list: 2D grid containing Perlin noise values.
    """
    # Create a grid to store the Perlin noise values
    grid = [[0] * width for _ in range(height)]
    # Iterate over each pixel in the grid
    for y in range(height):
        for x in range(width):
            # Calculate the coordinates in the noise grid
            xf = x / scale
            yf = y / scale
            xi = int(xf)
            yi = int(yf)
            # Calculate the fractional part of the coordinates
            tx = xf - xi
            ty = yf - yi

            # Determine the integer grid coordinates
            x0 = xi & (width - 1)
            x1 = (xi + 1) & (width - 1)
            y0 = yi & (height - 1)
            y1 = (yi + 1) & (height - 1)

            # Interpolate along x-axis
            sx = fade(tx)
            # Interpolate along y-axis
            sy = fade(ty)

            # Generate gradients for four corners of the cell
            n0 = gradient(grid[y0][x0], tx, ty)
            n1 = gradient(grid[y0][x1], tx - 1, ty)
            ix0 = lerp(n0, n1, sx)

            n0 = gradient(grid[y1][x0], tx, ty - 1)
            n1 = gradient(grid[y1][x1], tx - 1, ty - 1)
            ix1 = lerp(n0, n1, sx)

            # Interpolate along y-axis
            grid[y][x] = lerp(ix0, ix1, sy)

    return grid

def generate_perlin_noise(
    width,
    height,
    octaves = 6,
    persistence = 0.5,
):
    for y in range(height):
        for x in range(width):
            amplitude = 1
            noise_value = 0
            for _ in range(octaves):
                perlin_value = random.uniform(-1, +1)
                noise_value += perlin_value * amplitude
                amplitude *= persistence

            yield ((x, y), noise_value)

def main(argv=None):
    width = 50
    height = width
    screen = pygame.display.set_mode((800,800))
    surface = pygame.Surface((width, height))

    coords = it.product(range(width), range(height))

    noise_map = dict(generate_perlin_noise(width, height))

    # looks terrible
    #noise_map = {(x, y): simplex_noise_2d(x, y) for x, y in coords}

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
                else:
                    noise_map = dict(generate_perlin_noise(width, height))

        for (x, y), value in noise_map.items():
            # Convert floating-point color value to integer within valid range (0-255)
            color_value = int(value * 128 + 128)
            # Ensure color value stays within valid range
            color_value = max(0, min(255, color_value))
            color = (color_value, color_value, color_value)
            surface.set_at((x, y), color)

        pygame.transform.scale(surface, (800,)*2, screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
