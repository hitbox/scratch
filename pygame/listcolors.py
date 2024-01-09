import argparse
import collections as coll
import itertools as it
import math
import random
import re

from pprint import pprint

import pygamelib

from pygamelib import pygame

from pygame.color import THECOLORS

def render_color(font, color, name, scale):
    size = pygame.Vector2(font.size(name)).elementwise() * scale
    image = pygame.Surface(tuple(size), pygame.SRCALPHA)
    image.fill(color)
    rect = image.get_rect()
    text = font.render(name, True, 'white', color.lerp('black', 0.50))
    image.blit(text, text.get_rect(center=rect.center))
    return image

def get_blitables(font, window, colors, gap=0, scale=1):
    names = list(map(pygamelib.color_name, colors))
    sizes = zip(*map(font.size, names))
    text_size = pygame.Vector2(*map(max, sizes))
    text_size *= scale

    images = (pygame.Surface(text_size, pygame.SRCALPHA) for _ in colors)
    for image, color, name in zip(images, colors, names):
        rect = image.get_rect()
        color = pygame.Color(color)
        image.fill(color)
        text = font.render(name, True, 'white', color.lerp('black', 0.50))
        image.blit(text, text.get_rect(center=rect.center))
        yield (image, rect)

def gui(colors, names):
    assert len(colors) == len(names)
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('monospace', 20)

    ncols = math.isqrt(len(colors)) // 4

    sizes = list(map(pygame.Vector2, map(font.size, names)))
    images = [render_color(font, color, name, (1.25, 4)) for name, color in zip(names, colors)]
    rects = [image.get_rect() for image in images]
    pygamelib.arrange_columns(rects, ncols, 'centerx', 'centery')

    offset = pygame.Vector2()
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
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    offset += event.rel
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            x, y = pygame.mouse.get_pos()
            pygame.mouse.set_pos(x % window.width, y % window.height)
        screen.fill('black')
        for image, rect in zip(images, rects):
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

    items = ((name, color) for name, color in THECOLORS.items() if not exclude(name))
    names, colors = zip(*items)
    colors = list(map(pygame.Color, colors))

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
    gui(colors, names)

if __name__ == '__main__':
    main()
