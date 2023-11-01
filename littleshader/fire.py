import argparse
import contextlib
import functools
import math
import os
import random
import time

from itertools import chain
from itertools import cycle
from types import SimpleNamespace

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

FIRECOLORS = [
    'brown1',
    'crimson',
    'darkgoldenrod1',
    'darkorange',
    'deeppink',
    'firebrick1',
    'indianred',
    'ivory',
    'orangered',
    'red',
    'yellow',
]

class FlameSprite(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)
        self.rect = None
        self.position = None
        self.velocity = None
        self.acceleration = None
        self.radius = None
        self.color = None
        self.radius_countdown = 30
        self.radius_frames = 0

    def update_image_and_rect(self):
        self.image = circle_image(self.radius, tuple(self.color))
        self.rect = self.image.get_rect(center=self.position)

    def update(self, context):
        self.radius_frames += 1
        if self.radius_frames == self.radius_countdown:
            # change radius and update image
            self.radius_frames = 0
            self.radius -= 1
            self.update_image_and_rect()

        if not self.radius or self.rect.bottom < context.window.top:
            self.kill()
        else:
            self.velocity += self.acceleration
            self.position += self.velocity * context.elapsed
            self.rect.center = self.position


class Fire:

    def __init__(
        self,
        flames_per_frame,
        positions,
        velocities,
        radii,
        colors,
    ):
        self.flames_per_frame = flames_per_frame
        self.positions = positions
        self.velocities = velocities
        self.radii = radii
        self.colors = colors

    def _update(self, context):
        position = pygame.Vector2(next(self.positions))
        velocity = pygame.Vector2(next(self.velocities))
        radius = next(self.radii)
        color = next(self.colors)
        sprite = FlameSprite(context.sprites)
        sprite.position = position
        sprite.velocity = velocity
        sprite.acceleration = pygame.Vector2()
        sprite.radius = radius
        sprite.color = color
        sprite.update_image_and_rect()
        sprite.radius_countdown = random.randint(5, 10)

    def update(self, context):
        for _ in range(self.flames_per_frame):
            self._update(context)


def circle_image(radius, color):
    image = pygame.Surface((radius*2,)*2, flags=pygame.SRCALPHA)
    rect = image.get_rect()
    pygame.draw.circle(image, color, rect.center, radius)
    return image

def lerp(a, b, t):
    # position between a and b at time t
    return a * (1 - t) + b * t

def invlerp(a, b, x):
    # time of x between a and b
    return (x - a) / (b - a)

def remap(x, a, b, c, d):
    return x * (d-c) / (b-a) + c-a * (d-c) / (b-a)

def callinf(func, *args, **kwargs):
    while True:
        yield func(*args, **kwargs)

def random_position(top, right, bottom, left):
    x = random.randint(left, right)
    y = random.randint(top, bottom)
    return (x, y)

def painterly_circles(
    surf,
    c1,
    c2,
    ncircles,
    base_radius,
    var_radius,
    pixel_spread,
    pixels,
):
    for divisor in range(1, ncircles+1):
        radius = (base_radius / divisor) + (var_radius * (pixels / pixel_spread))
        color = c1.lerp(c2, divisor / ncircles)
        pygame.draw.circle(surf, color, surf.get_rect().midbottom, radius)

def background_generator(
    size,
    colors,
    ncircles,
    pixel_spread,
    base_radius,
    var_radius,
):
    """
    Generate circles from colors c1 to c2 in a painterly fashion.
    """
    assert pixel_spread > 0
    c1, c2 = colors
    up = range(-pixel_spread, +pixel_spread)
    down = range(+pixel_spread, -pixel_spread, -1)
    for pixels in chain(up, down):
        surf = pygame.Surface(size)
        surf.fill(c1)
        painterly_circles(
            surf,
            c1,
            c2,
            ncircles,
            base_radius,
            var_radius,
            pixel_spread,
            pixels,
        )
        yield surf

def run():
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 120
    font = pygame.font.SysFont('monospace', 24)
    context = SimpleNamespace(**locals())

    # cycle back and forth to make "glowing" background
    # created as iterated and then just iterated
    backgrounds = cycle(
        background_generator(
            size = window.size,
            colors = (
                pygame.Color('plum4'),
                pygame.Color('yellow'),
            ),
            ncircles = 8,
            pixel_spread = 50,
            base_radius = min(window.size),
            var_radius = min(window.size) / 128,
        )
    )

    sprites = pygame.sprite.Group()
    firerect = screen.get_rect(
        width=window.width / 2,
        midtop=window.midbottom,
    )
    minradius = min(firerect.size)//64
    maxradius = min(firerect.size)//8

    def fire_color(color_pairs):
        while True:
            between_color = random.randint(0, 10) / 10
            c1, c2 = next(color_pairs)
            color = c1.lerp(c2, between_color)
            color.a = random.randint(125, 150)
            yield color

    fire = Fire(
        flames_per_frame = 2,
        positions = callinf(
            random_position,
            firerect.top,
            firerect.right,
            firerect.bottom,
            firerect.left,
        ),
        velocities = callinf(
            lambda: (0, -random.randint(1, 20) / 50),
        ),
        radii = callinf(
            lambda: random.randint(minradius, maxradius),
        ),
        colors = fire_color(
            color_pairs = callinf(
                random.sample,
                list(map(pygame.Color, FIRECOLORS)),
                k = 2,
            ),
        ),
    )

    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

        context.__dict__.update(locals())
        fire.update(context)
        sprites.update(context)

        screen.blit(next(backgrounds), (0,0))
        sprites.draw(screen)
        lines = [
            f'{clock.get_fps()=:.2f}',
            f'{len(sprites)=}',
        ]
        images = [font.render(line, True, 'black') for line in lines]
        rects = [image.get_rect() for image in images]
        rects[0].bottomright = window.bottomright
        for r1, r2 in zip(rects, rects[1:]):
            r2.bottomright = r1.topright
        for image, rect in zip(images, rects):
            screen.blit(image, rect)
        pygame.display.flip()

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()
