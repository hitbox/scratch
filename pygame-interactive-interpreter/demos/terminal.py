# Thinking we need another "thing" for emulating a terminal. Just input and
# output display.
from engine.engine import Engine
from engine.engine import stopengine
from lib.cli import simple_parser
from lib.external import pygame
from lib.font import PygameFont
from lib.screen import Screen
from scenes.base import BaseScene

class TerminalScene(BaseScene):
    """
    Demo of a terminal like thing with Python and pygame.
    """

    def enter(self):
        pass

    def exit(self):
        pass

    def __init__(self, screen_size):
        if screen_size is None:
            screen_size = (800, 600)
        self.screen = Screen(screen_size)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            stopengine()

    def update(self, events):
        for event in events:
            self.on_event(event)


def main(argv=None):
    class_ = TerminalScene
    parser = simple_parser(description=class_.__doc__)
    args = parser.parse_args(argv)

    engine = Engine()
    scene = class_(args.screen_size)
    engine.run(scene)

if __name__ == '__main__':
    main()
