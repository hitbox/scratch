import argparse
import itertools as it

import pygamelib

from pygamelib import pygame

class imagescaler:

    def __init__(self, scale):
        self.scale = scale

    def __call__(self, image):
        width, height = image.get_size()
        return pygame.transform.scale(image, (width * self.scale, height * self.scale))


def sliceimage(image, size):
    width, height = size
    image_width, image_height = image.get_size()
    for x in range(0, image_width, width):
        for y in range(0, image_height, height):
            yield image.subsurface(x, y, width, height)

def autoslice(image, slice_):
    image_width, image_height = image.get_size()
    width, height = slice_
    if width < 0:
        width = image_width
    if height < 0:
        height = image_height
    width = min(width, image_width)
    height = min(height, image_height)
    return sliceimage(image, (width, height))

def run(
    display_size,
    image_file,
    scale,
    slice_,
    animation_delay,
    flash_delay,
    flash_color,
    outline_color,
):
    screen = pygame.display.set_mode(display_size)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 60

    image = pygame.image.load(image_file)
    images = list(map(imagescaler(scale), autoslice(image, slice_)))
    masks = list(map(pygame.mask.from_surface, images))
    flashes = [mask.to_surface(setcolor=flash_color, unsetcolor=None) for mask in masks]

    scaler = imagescaler(scale)
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

        if outline_color:
            delta = pygame.Vector2(positioned.topleft)
            points = list(delta + point for point in mask.outline())
            pygame.draw.lines(screen, outline_color, False, points, 8)

        pygame.display.flip()

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'image',
        type = argparse.FileType(),
    )
    parser.add_argument(
        '--scale',
        type = int,
        default = 6,
    )
    parser.add_argument(
        '--slice',
        type = pygamelib.sizetype(),
    )
    parser.add_argument(
        '--animation-delay',
        type = int,
        default = 100,
    )
    parser.add_argument(
        '--flash-delay',
        type = int,
        default = 125,
    )
    parser.add_argument(
        '--flash-color',
        default = 'linen',
    )
    parser.add_argument(
        '--outline-color',
    )
    args = parser.parse_args(argv)
    run(
        args.display_size,
        args.image,
        args.scale,
        args.slice,
        args.animation_delay,
        args.flash_delay,
        args.flash_color,
        args.outline_color,
    )

if __name__ == '__main__':
    main()

# 2024-02-27 Tue.
# - want to make swiping effects from image masks
