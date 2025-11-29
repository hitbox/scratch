"""
Messing with y-sorting for topdown kind of thing. centery seems to look best.
"""
import argparse
import contextlib
import os
import random

from operator import attrgetter

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

def copy_rect(source, **kwargs):
    rect = source.copy()
    for key, value in kwargs.items():
        setattr(rect, key, value)
    return rect

def attrtype(string):
    if not string.startswith('rect.'):
        raise ValueError('Must be an attribute of the rect attribute')
    return string

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('attr', type=attrtype)
    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)

    sort_key = attrgetter(args.attr)

    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    frame = screen.get_rect()
    clock = pygame.time.Clock()

    sprites = pygame.sprite.Group()
    spawn = copy_rect(frame, size=(500, 500), center=frame.center)

    for _ in range(100):
        sprite = pygame.sprite.Sprite(sprites)
        sprite.rect = pygame.Rect((0,0), (50, 50))
        sprite.image = pygame.Surface(sprite.rect.size)
        sprite.image.fill('green')
        x = random.randint(spawn.left, spawn.right)
        y = random.randint(spawn.top, spawn.bottom)
        sprite.rect.center = (x, y)

    player = pygame.sprite.Sprite(sprites)
    player.rect = copy_rect(frame, size=(100,100), center=frame.center)
    player.image = pygame.Surface(player.rect.size, flags=pygame.SRCALPHA)
    pygame.draw.circle(player.image, 'red', (50, 50), 25, 0)

    move_speed = 0.25

    elapsed = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                pass

        pressed = pygame.key.get_pressed()
        dx = dy = 0
        if pressed[pygame.K_UP]:
            dy = -move_speed
        if pressed[pygame.K_DOWN]:
            dy = move_speed
        if pressed[pygame.K_RIGHT]:
            dx = move_speed
        if pressed[pygame.K_LEFT]:
            dx = -move_speed

        player.rect.x += dx * elapsed
        player.rect.y += dy * elapsed

        screen.fill('black')
        sorted_sprites = sorted(sprites, key=sort_key)
        screen.blits([(s.image, s.rect) for s in sorted_sprites])

        pygame.display.flip()
        elapsed = clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
