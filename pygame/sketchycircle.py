import argparse
import contextlib
import itertools
import math
import os
import random

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

def lerp(a, b, t):
    return a * (1 - t) + b * t

def remap(x, a, b, c, d):
    return x * (d-c) / (b-a) + c-a * (d-c) / (b-a)

def run(background, outline, outline2=None):
    screen = pygame.display.set_mode((512,)*2)
    window = screen.get_rect()

    if outline2 is None:
        outline2 = outline
    outline_radius = min(window.size)/3

    def draw():
        screen.fill(background)
        colors = [outline, background]
        for i in range(8):
            color1 = colors[(i+0) % len(colors)]
            color2 = colors[(i+1) % len(colors)]

            offset = random.randint(1, 3)
            color_t = remap(offset, 1, 3, 0, 1)
            color = color1.lerp(color2, color_t)

            angle = math.radians(random.randrange(360))
            x = window.centerx + math.cos(angle) * offset
            y = window.centery + math.sin(angle) * offset
            width = random.randint(1, 2)
            pygame.draw.circle(screen, color, (x, y), outline_radius, width)

    draw()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                else:
                    draw()
        pygame.display.flip()

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--background', default='black', type=pygame.Color)
    parser.add_argument('--outline', default='azure', type=pygame.Color)
    parser.add_argument('--outline2', default='snow', type=pygame.Color)
    args = parser.parse_args(argv)
    run(args.background, args.outline)

if __name__ == '__main__':
    main()
