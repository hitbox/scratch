import math

import pygamelib

from pygamelib import pygame

class Demo(pygamelib.DemoBase):

    def __init__(self, drawables):
        self.drawables = drawables
        self.offset = pygame.Vector2()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.engine.stop()

    def do_mousemotion(self, event):
        if event.buttons[0]:
            self.offset -= event.rel
            pygamelib.post_videoexpose()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        for drawable in self.drawables:
            drawable.draw(self.screen, 'white', 1, self.offset)
        pygame.display.flip()


def run(display_size, debug, cleft_angle=None):
    window = pygame.Rect((0,0), display_size)
    pygame.display.init()
    pygame.font.init()
    engine = pygamelib.Engine()

    heart_rect = window.inflate((-min(window.size)*.50,)*2)
    heart_shape = pygamelib.HeartShape(cleft_angle=cleft_angle)
    heart = list(heart_shape(heart_rect))
    state = Demo(heart)

    pygame.display.set_mode(display_size)
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('--cleft-angle', type=int)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args(argv)
    run(args.display_size, args.debug, args.cleft_angle)

if __name__ == '__main__':
    main()
