import argparse
import itertools as it
import random
import re

from pprint import pprint

import pygamelib

from pygamelib import pygame

from pygame.color import THECOLORS

def get_blitables(font, window, color_items):
    text_sizes = (font.size(name) for name, _ in color_items)
    text_size = pygame.Vector2(*map(max, zip(*text_sizes)))
    text_size.x *= 2
    text_size.y *= 3

    images = [pygame.Surface(text_size, pygame.SRCALPHA) for _ in color_items]
    rects = [image.get_rect() for image in images]
    text_background = pygame.Color(0,0,0,20)
    for image, rect, (name, color) in zip(images, rects, color_items):
        color = pygame.Color(color)
        image.fill(color)
        text = font.render(name, True, 'white', color.lerp((0,0,0), 0.25))
        image.blit(text, text.get_rect(center=rect.center))

    rects[0].midtop = window.midtop
    for r1, r2 in it.pairwise(rects):
        r2.midtop = (r1.centerx, r1.bottom + 10)

    return zip(images, rects)

def gui(colors):
    color_items = [(color, pygamelib.color_name(color)) for color in colors]
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('monospace', 24)

    blitables = list(get_blitables(font, window, color_items))
    max_bottom = max(rect.bottom for _, rect in blitables)

    offset = pygame.Vector2((0,-max_bottom // 2 - window.height // 2))

    y_speed = max(rect.height for image, rect in blitables) * 2

    framerate = 60
    elapsed = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEWHEEL:
                offset.y += event.y * y_speed
        screen.fill('black')
        for image, rect in blitables:
            screen.blit(image, offset + rect.topleft)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--print', action='store_true')

    filtering_group = parser.add_mutually_exclusive_group()
    filtering_group.add_argument('--exclude')
    filtering_group.add_argument('--colorful', action='store_true')

    ordering_group = parser.add_mutually_exclusive_group()
    ordering_group.add_argument('--shuffle', action='store_true')
    for space_name in pygamelib.ColorSpace.spaces:
        ordering_group.add_argument(f'--{space_name}', action='store_true')
    args = parser.parse_args(argv)

    if not args.exclude and not args.colorful:
        exclude = lambda name: False
    elif args.exclude or args.colorful:
        if args.exclude:
            exclude = re.compile(args.exclude).search
        else:
            def exclude(name):
                return not pygamelib.interesting_color(name)

    colors = [name for name, color in THECOLORS.items() if not exclude(name)]

    if args.shuffle:
        random.shuffle(colors)
    else:
        for space_name in pygamelib.ColorSpace.spaces:
            flag = getattr(args, space_name)
            if flag:
                color_key = pygamelib.ColorSpace(space_name)
                colors = sorted(colors, key=color_key)
                break

    if args.print:
        pprint([key for key, _ in colors])
    gui(colors)

if __name__ == '__main__':
    main()
