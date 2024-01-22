from itertools import cycle

from engine.engine import Engine
from engine.engine import stopengine
from lib.cli import simple_parser
from lib.external import pygame
from lib.font import PygameFont
from lib.screen import Screen
from misc.cycle import Delayed
from scenes.base import BaseScene

class HelloWorldScene(BaseScene):
    # XXX:
    # * ok, 2021-10-10, this helloworld is good enough for now. going to
    #   explore other things and see how lib and other evolve.

    def __init__(self, screen_size):
        if screen_size is None:
            screen_size = (800, 600)
        self.screen = Screen(screen_size)
        self.clock = pygame.time.Clock()
        pygame.font.init()
        # XXX:
        # * don't know what to do about pygame.font
        # * would like it to be more nicely abstracted like Screen
        self.font = pygame.font.SysFont('monospace', 110)
        self.image = self.font.render('Hello World', True, (200,)*3)
        self.dest = self.image.get_rect(center=self.screen.rect.center)

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        # tick
        elapsed_ms = self.clock.tick(60)
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stopengine()
        # draw
        self.screen.clear()
        self.screen.blit(self.image, self.dest)
        self.screen.update()


def main(argv=None):
    """
    Print "Hello World"
    """
    parser = simple_parser(description=main.__doc__)
    args = parser.parse_args(argv)

    engine = Engine()
    scene = HelloWorldScene(args.screen_size)
    engine.run(scene)

if __name__ == '__main__':
    main()
