import argparse
import contextlib
import itertools as it
import operator as op
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

from pygame.color import THECOLORS

class _colorkey:

    def __init__(self):
        self.keys = ['cmy', 'hsl', 'hsv', 'rgb']

    def __getattr__(self, name):
        assert name in self.keys
        if name == 'rgb':
            return op.attrgetter(*name)

        if name != 'cmy':
            # the others include an alpha...
            name += 'a'

        _g = op.attrgetter(name)
        def g(color):
            # ...but we only want the coords
            return _g(color)[:3]
        return g


colorkey = _colorkey()


class ColorSorter:

    def __init__(self, n, key, origin, items):
        self.n = n
        self.key = key
        self.origin = origin
        self.items = items

    def __iter__(self):
        coords = getattr(colorkey, self.key)
        origin = pygame.Vector3(coords(self.origin))

        def pos(color):
            return coords(pygame.Color(color))

        def color_distance(color):
            return origin.distance_to(pos(color))

        def key(item):
            name, color = item
            return color_distance(color)

        result = sorted(self.items, key=key)

        def text(name, color):
            return f'{name} {color_distance(color):.2f}'

        result = [(text(name, color), color) for name, color in result]
        return iter(result[:self.n])


def blittables(font, window, color_sorter):
    sizes = (font.size(name) for name, _ in color_sorter)
    size = pygame.Vector2(*map(max, zip(*sizes)))
    size *= 2

    images = [pygame.Surface(size) for _ in color_sorter]
    rects = [image.get_rect() for image in images]
    for image, rect, (name, color) in zip(images, rects, color_sorter):
        image.fill(color)
        text = font.render(name, True, 'white', color)
        image.blit(text, text.get_rect(center=rect.center))

    for r1, r2 in it.pairwise(rects):
        r2.midtop = r1.midbottom

    origin = rects[0].unionall(rects[1:])
    dest = origin.copy()
    dest.center = window.center
    delta = pygame.Vector2(dest.topleft) - origin.topleft
    for rect in rects:
        rect.topleft += delta
    return zip(images, rects)

def gui(color_sorter):
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('monospace', 24)
    keys = it.cycle(colorkey.keys)

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
                elif event.key == pygame.K_DOWN:
                    color_sorter.key = next(keys)
        screen.fill('black')
        for image, rect in blittables(font, window, color_sorter):
            screen.blit(image, rect)
        text = f'{color_sorter.key=}'
        text_image = font.render(text, True, 'white')
        screen.blit(text_image, text_image.get_rect(bottomright=window.bottomright))
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    """
    Find a pygame color.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('color', type=pygame.Color)
    parser.add_argument('-n', type=int, default=3)
    parser.add_argument(
        '--space',
        choices = ['cmy', 'hsl', 'hsv', 'rgb'],
        default = 'rgb',
    )
    parser.add_argument(
        '--gui',
        action = 'store_true',
    )
    args = parser.parse_args(argv)

    color_sorter = ColorSorter(args.n, args.space, args.color, THECOLORS.items())
    if args.gui:
        gui(color_sorter)
    else:
        for name, color in color_sorter:
            print(name, color)

if __name__ == '__main__':
    main()
