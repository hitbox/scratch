import argparse
import contextlib
import math
import os
import random

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

def poisson_probability_mass(k, lambda_parameter):
    return (lambda_parameter ** k) * math.exp(-lambda_parameter) / math.factorial(k)

def generate_poisson_sample(lambda_parameter, size):
    for _ in range(size):
        L = math.exp(-lambda_parameter)
        k = 0
        p = 1
        u = 1.0
        if lambda_parameter != 0:
            u -= random.random()
        while p > L:
            k += 1
            p *= u
        yield k - 1

def run():
    WIDTH, HEIGHT = 600, 400
    FPS = 60

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    lambda_parameter = 3.0
    sample_size = 1000

    # Generate a random sample from the Poisson distribution
    random_sample = list(generate_poisson_sample(lambda_parameter, sample_size))

    # Calculate PMF values for specific k values
    k_values = range(11)
    pmf_values = [poisson_probability_mass(k, lambda_parameter) for k in k_values]

    # Normalize PMF values for display
    max_pmf = max(pmf_values)
    pmf_values_normalized = [val / max_pmf * (HEIGHT - 50) for val in pmf_values]

    bar_width = 30
    x_offset = 50
    running = True
    while running:
        screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        for i, val in enumerate(pmf_values_normalized):
            x = x_offset + i * (bar_width + 10)
            y = HEIGHT - val - 20
            r = (x, y, bar_width, val)
            pygame.draw.rect(screen, 'brown', r)
        pygame.display.flip()
        clock.tick(FPS)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()
