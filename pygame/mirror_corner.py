import argparse
import math
import random

from itertools import cycle
from types import SimpleNamespace

import pygamelib

from pygamelib import pygame

class RandomPixels:

    def __init__(self, randomizer):
        self.choices = [
            'randint_pixel',
            'weibullvariate_pixel',
            'uniform_pixel',
            'triangular_pixel',
            'vonmisesvariate_pixel',
        ]
        self.randomizer = randomizer

    def randint_pixel(self, size):
        x = random.randint(0, size[0])
        y = random.randint(0, size[1])
        return (x, y)

    def weibullvariate_pixel(self, size):
        x = random.weibullvariate(1, 1)
        y = random.weibullvariate(1, 1)
        return tuple(map(int, remap_pixel(size, x, y)))

    def uniform_pixel(self, size):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        return tuple(map(int, remap_pixel(size, x, y)))

    def triangular_pixel(self, size):
        x = random.triangular()
        y = random.triangular()
        return tuple(map(int, remap_pixel(size, x, y)))

    def vonmisesvariate_pixel(self, size):
        x = random.vonmisesvariate(0, 0) / math.tau
        y = random.vonmisesvariate(0, 0) / math.tau
        return tuple(map(int, remap_pixel(size, x, y)))

    def generate(self, size, n):
        randfunc = getattr(self, self.randomizer)
        pixels = set()
        while len(pixels) < n and (pos := randfunc(size)) not in pixels:
            yield pos
            pixels.add(pos)


def remap_pixel(size, x, y):
    width, height = size
    x = pygamelib.remap(x, 0, 1, 0, size[0])
    y = pygamelib.remap(y, 0, 1, 0, size[1])
    return (x, y)

def shader(size, pos):
    x, y = pos
    w, h = size
    return math.sin(x/w)==0 or math.sin(y/h)==0

def scale(iterable, by_val):
    for x in iterable:
        yield x * by_val

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 60
    pygame.font.init()
    font = pygame.font.SysFont('monospace', 24)

    settings = SimpleNamespace(
        size = (16,) * 2,
        scale = 16,
    )
    settings.n = (settings.size[0] * settings.size[1]) // 2

    pixelgenerator = RandomPixels('randint_pixel')
    pixelgenerator.randfuncs = cycle(pixelgenerator.choices)

    image = None

    def _update_image():
        nonlocal image
        topleft_pixels = list(pixelgenerator.generate(settings.size, settings.n))
        right_and_bottom_pixels = list(
            pixelgenerator.generate(settings.size, math.isqrt(settings.n))
        )
        right_pixels = [(settings.size[0] - x, y) for x, y in right_and_bottom_pixels]
        bottom_pixels = [(x, settings.size[1] - y) for x, y in right_and_bottom_pixels]
        bottomright_pixels = list(
            (settings.size[0] - x, settings.size[1] - y)
            for x, y in pixelgenerator.generate(
                settings.size, math.isqrt(math.isqrt(settings.n))
            )
        )
        pixels = topleft_pixels + right_pixels + bottom_pixels + bottomright_pixels
        mirrored = pygame.Surface(tuple(map(lambda x: x * 2, settings.size)))
        for pixel in pixels:
            mirrored.set_at(pixel, 'white')
        final_size = tuple(scale(settings.size, settings.scale))
        image = pygame.transform.scale(mirrored, final_size)

    def _update_image():
        nonlocal image
        size = settings.size
        width, height = size
        tile = pygame.Surface(size)
        color = 'azure'
        for y in range(height):
            for x in range(width):
                pos = (x, y)
                if shader(size, pos):
                    tile.set_at(pos, color)
                    tile.set_at((width - x, y), color)
                    tile.set_at((x, height - y), color)
                    tile.set_at((width - x, height - y), color)
        image = pygame.transform.scale(
            tile,
            tuple(scale(settings.size, settings.scale))
        )

    _update_image()

    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                else:
                    if event.key == pygame.K_SPACE:
                        pixelgenerator.randomizer = next(pixelgenerator.randfuncs)
                    _update_image()
        screen.fill('black')

        screen.blit(image, image.get_rect(topleft=window.topleft))
        # TODO
        # - mirror these too
        # - once the falloff thing is working
        tmp = pygame.transform.flip(image, 1, 0)
        screen.blit(tmp, tmp.get_rect(topright=window.topright))

        tmp = pygame.transform.flip(image, 1, 1)
        screen.blit(tmp, tmp.get_rect(bottomright=window.bottomright))

        tmp = pygame.transform.flip(image, 0, 1)
        screen.blit(tmp, tmp.get_rect(bottomleft=window.bottomleft))

        text_image = font.render(f'{pixelgenerator.randomizer}', True, 'azure')
        screen.blit(text_image, text_image.get_rect(center=window.center))

        pygame.display.flip()

if __name__ == '__main__':
    main()

# 2023-12-14
# - https://www.reddit.com/r/pygame/comments/18i6wnn/geenna_demo_is_now_available_here/
# - demo shows mirrored tile things in the corners
