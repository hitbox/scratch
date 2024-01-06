import argparse
import contextlib
import itertools as it
import os
import random
import re

from pprint import pprint

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

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

def gui(color_items):
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('monospace', 24)

    blitables = list(get_blitables(font, window, color_items))
    max_bottom = max(rect.bottom for _, rect in blitables)

    offset = pygame.Vector2((0,-max_bottom // 2 - window.height // 2))

    y_speed = max(rect.height for image, rect in blitables) * 1.5

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

def sort_key(args):
    if args.rgb:
        def key(item):
            name, color = item
            return color[:3]
    elif args.cmy:
        def key(item):
            name, color = item
            color = pygame.Color(color)
            return color.cmy
    elif args.hsl:
        def key(item):
            name, color = item
            color = pygame.Color(color)
            return color.hsla[:3]
    elif args.hsv:
        def key(item):
            name, color = item
            color = pygame.Color(color)
            return color.hsva[:3]
    elif args.hue:
        def key(item):
            name, color = item
            color = pygame.Color(color)
            hue, _, _, _ = color.hsva
            return hue
    return key

def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--print', action='store_true')

    filtering_group = parser.add_mutually_exclusive_group()
    filtering_group.add_argument('--exclude')
    filtering_group.add_argument('--colorful', action='store_true')

    ordering_group = parser.add_mutually_exclusive_group()
    ordering_group.add_argument('--shuffle', action='store_true')
    ordering_group.add_argument('--cmy', action='store_true')
    ordering_group.add_argument('--hsl', action='store_true')
    ordering_group.add_argument('--hsv', action='store_true')
    ordering_group.add_argument('--rgb', action='store_true')
    ordering_group.add_argument('--hue', action='store_true')

    args = parser.parse_args(argv)

    if not args.exclude and not args.colorful:
        exclude = lambda name: False
    elif args.exclude or args.colorful:
        pattern = (
            args.exclude
            or
            r'gr[ae]y|white|black|light|medium|dark|\d|red|green|blue'
        )
        exclude = re.compile(pattern).search

    colors = [(name, color) for name, color in THECOLORS.items() if not exclude(name)]

    if args.shuffle:
        random.shuffle(colors)
    elif any([args.cmy, args.hsl, args.hsv, args.rgb, args.hue]):
        colors = sorted(colors, key=sort_key(args))

    if args.print:
        pprint([key for key, _ in colors])
    gui(colors)

if __name__ == '__main__':
    main()
