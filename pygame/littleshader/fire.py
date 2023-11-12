import argparse
import contextlib
import os
import random

from itertools import chain
from itertools import cycle
from itertools import pairwise
from operator import attrgetter
from types import SimpleNamespace

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

FIRECOLORS = [
    'brown1',
    #'crimson',
    #'darkgoldenrod1',
    #'darkorange',
    #'deeppink',
    'firebrick1',
    'indianred',
    #'ivory',
    'orangered',
    #'red',
    #'yellow',
]

class Checkbox:

    def __init__(self, value, checked, label=None):
        self.value = value
        self.checked = checked
        self.label = label


class CheckboxSprite(pygame.sprite.Sprite):

    def update_image_and_rect(self, size, line_color, position=None):
        if position is None:
            position = {}
        position = dict(position)
        self.image = pygame.Surface(size, flags=pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, line_color, self.rect, 1)
        if self.checkbox.checked:
            cross_rect = self.rect.inflate((-min(size)//4,)*2)
            draw_cross(self.image, line_color, cross_rect)
        for key, value in position.items():
            setattr(self.rect, key, value)

    def on_click(self):
        self.checkbox.checked = not self.checkbox.checked


class Select:

    def __init__(self, choices=None):
        if choices is None:
            choices = []
        self.choices = choices


class FlameSprite(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)
        self.rect = None
        self.position = None
        self.velocity = None
        self.acceleration = None
        self.radius = None
        self.color = None
        self.radius_countdown = None
        self.radius_frames = 0

    def update_shape(
        self,
        radius,
        color,
    ):
        self.radius = radius
        self.color = color

    def update_dynamics(
        self,
        position,
        velocity,
        acceleration,
    ):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration

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
        flame = FlameSprite(context.sprites)
        flame.update_shape(
            radius = next(self.radii),
            color = next(self.colors),
        )
        flame.update_dynamics(
            position = pygame.Vector2(next(self.positions)),
            velocity = pygame.Vector2(next(self.velocities)),
            acceleration = pygame.Vector2(),
        )
        flame.update_image_and_rect()
        flame.radius_countdown = random.randint(5, 10)

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

def draw_cross(surf, line_color, rect=None):
    pygame.draw.line(surf, line_color, rect.topleft, rect.bottomright)
    pygame.draw.line(surf, line_color, rect.bottomleft, rect.topright)

def instance_is(class_or_tuple):
    def _instance_is(obj):
        return isinstance(obj, class_or_tuple)
    return _instance_is

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
                pygame.Color('chocolate'),
            ),
            ncircles = 8,
            pixel_spread = 50,
            base_radius = min(window.size),
            var_radius = min(window.size) / 128,
        )
    )

    sprites = pygame.sprite.Group()

    select = Select()
    for color_name in FIRECOLORS:
        checkbox = Checkbox(
            value = pygame.Color(color_name),
            checked = True,
            label = color_name,
        )
        select.choices.append(checkbox)
        checkbox_sprite = CheckboxSprite(sprites)
        checkbox_sprite.checkbox = checkbox
        checkbox_sprite.update_image_and_rect((20,)*2, 'azure')

    checkbox_sprites = list(filter(instance_is(CheckboxSprite), sprites))
    for checkbox_sprite1, checkbox_sprite2 in pairwise(checkbox_sprites):
        checkbox_sprite2.rect.topright = checkbox_sprite1.rect.bottomright
        for checkbox_sprite in [checkbox_sprite1, checkbox_sprite2]:
            checkbox_sprite.label_sprite = pygame.sprite.Sprite(sprites)
            checkbox_sprite.label_sprite.image = font.render(
                checkbox_sprite.checkbox.label,
                True,
                'azure',
            )
            checkbox_sprite.label_sprite.rect = checkbox_sprite.label_sprite.image.get_rect(
                topleft = checkbox_sprite.rect.topright,
            )

    # XXX
    # - left off here
    # - running into problems with selecting things
    # - need to get the checkboxes and labels here
    rect = pygame.Rect((0,)*4).unionall(list(map(attrgetter('rect'), checkbox_sprites)))

    # flames and fire
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
        flames_per_frame = 8,
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
            random.randint,
            minradius,
            maxradius,
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
