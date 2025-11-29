import argparse
import contextlib
import os
import random

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class Assets:

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.names = {}

    def named_load(self, rel_path, name):
        self.names[name] = pygame.image.load(os.path.join(self.base_dir, rel_path))

    def __getitem__(self, name):
        return self.names[name]


class Health:

    def __init__(self, value, max_value):
        self.value = value
        self.max_value = max_value


def main():
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    frame = screen.get_rect()
    clock = pygame.time.Clock()

    assets = Assets('/home/hitbox/Downloads/Kenney Game Assets/Kenney Game Assets All-in-1 3.1.0/')
    assets.named_load(
        '2D assets/New Platformer Pack/Sprites/Tiles/Default/hud_heart_half.png',
        'half_heart'
    )

    assets.named_load(
        '2D assets/Emote Pack/PNG/Vector/Style 8/emote_heart.png',
        'emote_heart',
    )

    assets.named_load(
        '2D assets/Emote Pack/PNG/Vector/Style 8/emote_heartBroken.png',
        'emote_broken_heart',
    )

    health = Health(value=5, max_value=10)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                pass

        screen.fill('black')
        x = 0
        for index in range(health.max_value):
            if health.value > index:
                image = assets['emote_heart']
            else:
                image = assets['emote_broken_heart']
            screen.blit(image, (x, 0))
            x += image.get_width()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
