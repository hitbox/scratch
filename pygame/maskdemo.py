import argparse
import functools
import itertools as it

import pygamelib

from pygamelib import pygame

def run(
    display_size,
    framerate,
    spritesheet,
    animation_delay,
    flash_delay,
    flash_color,
    outline_style,
):
    screen = pygame.display.set_mode(display_size)
    window = screen.get_rect()
    clock = pygame.time.Clock()

    images = spritesheet.get_images()
    scaler = functools.partial(pygamelib.scale, spritesheet.scale)
    images = list(map(scaler, images))
    masks = list(map(pygame.mask.from_surface, images))
    flashes = [mask.to_surface(setcolor=flash_color, unsetcolor=None) for mask in masks]

    masks = it.cycle(masks)
    images = it.cycle(images)
    flashes = it.cycle(flashes)
    flash_time = 0

    countdown = 0
    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif event.key == pygame.K_SPACE and flash_time == 0:
                    flash_time = flash_delay
        screen.fill('indigo')
        if countdown - elapsed < 0:
            countdown = 0
        else:
            countdown -= elapsed
        if countdown == 0:
            image = next(images)
            flash = next(flashes)
            mask = next(masks)
            countdown = animation_delay

        if flash_time > 0:
            draw_image = flash
            if flash_time - elapsed < 0:
                flash_time = 0
            else:
                flash_time -= elapsed
        else:
            draw_image = image

        positioned = draw_image.get_rect(center=window.center)
        screen.blit(draw_image, positioned)

        if outline_style:
            width, color = outline_style
            delta = pygame.Vector2(positioned.topleft)
            points = list(delta + point for point in mask.outline())
            pygame.draw.lines(screen, color, False, points, width)

        pygame.display.flip()

def argument_parser():
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'spritesheet',
        type = pygamelib.SpriteSheet.from_shorthand,
    )
    parser.add_argument(
        '--animation-delay',
        type = int,
        default = 100,
        help = 'Time in milliseconds before next frame.',
    )
    parser.add_argument(
        '--flash-delay',
        type = int,
        default = 125,
        help = 'Cooldown in milliseconds after flashing.',
    )
    parser.add_argument(
        '--flash-color',
        default = 'linen',
    )
    parser.add_argument(
        '--outline-style',
        type = pygamelib.BorderStyle.from_shorthand,
    )
    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)
    run(
        args.display_size,
        args.framerate,
        args.spritesheet,
        args.animation_delay,
        args.flash_delay,
        args.flash_color,
        args.outline_style,
    )

if __name__ == '__main__':
    main()

# 2024-02-27 Tue.
# - want to make swiping effects from image masks
