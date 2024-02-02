import random

import pygamelib

from pygamelib import pygame

class ImageState(pygamelib.DemoBase):

    def __init__(self, image):
        self.image = image

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        self.screen.blit(self.image, self.image.get_rect(center=self.window.center))
        pygame.display.flip()


def run(display_size):
    window = pygame.Rect((0,0), display_size)

    size = tuple(d*.5 for d in display_size)
    rect = pygame.Rect((0,0), size)
    image = pygame.Surface(size)
    image.fill('red')

    partialcircle_size = tuple(d * 0.95 for d in size)
    partialcircle = pygame.Surface(partialcircle_size, pygame.SRCALPHA)
    partialcircle.fill(pygame.Color('red').lerp('tomato', .75))

    # TODO
    # - generic system to load with variables
    # - variables used to construct this image
    # - display and modify variables

    partialcircle_rect = partialcircle.get_rect()
    radius = min(partialcircle_size) * .95
    pygame.draw.circle(
        partialcircle,
        'red',
        (
            partialcircle_rect.centerx + partialcircle_rect.width * .20,
            partialcircle_rect.bottom + partialcircle_rect.height * .40,
        ),
        radius
    )
    image.blit(partialcircle, partialcircle.get_rect(center=rect.center))

    state = ImageState(image)
    pygame.display.set_mode(display_size)
    engine = pygamelib.Engine()
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args.display_size)

if __name__ == '__main__':
    main()

# 2024-01-31
# - trying to produce a shiny surface looking image
# - like this:
#   https://clipart-library.com/clipart/BTar9Bopc.htm
