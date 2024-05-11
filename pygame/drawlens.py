import argparse
import io
import sys

import pygamelib

from pygamelib import pygame

class HAL9000:

    def __init__(self, bright, background, ring):
        self.bright = bright
        self.background = background
        self.ring = ring

    def __call__(self, image, offset=None):
        if offset is None:
            offset = (0, 0)
        ox, oy = offset
        rect = image.get_rect()
        cx, cy = rect.center
        radius = min(rect.size) // 2

        def circle(color, pos, radius_percent, width_percent=0):
            pygame.draw.circle(
                image,
                color,
                pos,
                int(radius * radius_percent),
                int(radius * width_percent),
            )

        circle(self.bright, (cx + ox * 0.005, cy + oy * 0.005), 1.0)
        circle(self.background, (cx + ox * 0.01, cy + oy * 0.01), 0.95)
        circle(self.ring, (cx + ox * 0.01, cy + oy * 0.01), 0.95, 0.05)
        circle(self.ring, (cx + ox * 0.03, cy + oy * 0.03), 0.6, 0.2)
        circle(self.ring, (cx + ox * 0.10, cy + oy * 0.10), 0.1)

        pos = (
            cx - radius * 0.3 + ox * 0.01,
            cy - radius * 0.4 + oy * 0.01,
        )
        pygame.draw.circle(image, self.bright, pos, radius*0.15)

        pos = (
            cx - radius * 0.05 + ox * 0.01,
            cy - radius * 0.5 + oy * 0.01,
        )
        pygame.draw.circle(image, self.bright, pos, radius*0.05)


def interactive(size, hal9k):
    screen = pygame.display.set_mode(size)
    window = screen.get_rect()
    cx, cy = window.center
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        mx, my = pygame.mouse.get_pos()
        ox = mx - cx
        oy = my - cy
        screen.fill('black')
        hal9k(screen, (ox, oy))
        pygame.display.flip()

def main(argv=None):
    """
    Draw a lens-eyeball like HAL 9000.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--size',
        type = pygamelib.sizetype(),
        default = '500',
    )
    parser.add_argument(
        '--offset',
        type = pygamelib.sizetype(),
        default = '0',
    )
    parser.add_argument(
        '--pipe',
        action = 'store_true',
    )
    parser.add_argument(
        '--bright',
        default = 'white',
    )
    parser.add_argument(
        '--background',
        default = 'grey30',
    )
    parser.add_argument(
        '--ring',
        default = 'grey5',
    )
    args = parser.parse_args(argv)

    hal9k = HAL9000(args.bright, args.background, args.ring)

    if args.pipe:
        image = pygame.Surface(args.size)
        hal9k(image, args.offset)
        with io.BytesIO() as output:
            pygame.image.save(image, output, 'png')
            sys.stdout.buffer.write(output.getvalue())
    else:
        interactive(args.size, hal9k)

if __name__ == '__main__':
    main()
