import argparse
import itertools as it
import math
import operator as op
import random

import pygamelib

from pygamelib import pygame

class Demo(pygamelib.DemoBase):

    def __init__(self):
        self.frame_count = 0

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        a = 1.5
        b = -0.7
        theta = 0
        while theta <= math.tau:
            r = 1
            time = self.frame_count * 0.01
            x = (r * math.cos(theta)) / (1 - a * r * math.cos(theta + time * 2.5))
            y = (r * math.sin(theta)) / (1 - b * r * math.sin(theta + time * 2.5))
            px = pygamelib.remap(x, -1.5, 1.5, -self.window.width / 2, self.window.width / 2);
            py = pygamelib.remap(y, -1.5, 1.5, -self.window.height / 2, self.window.height / 2);
            self.screen.set_at(tuple(map(int, (px, py))), 'white')
            theta += 0.005
        pygame.display.flip()
        self.frame_count += 1

def run(display_size):
    state = Demo()
    pygame.display.set_mode(display_size)
    engine = pygamelib.Engine()
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args.display_size)

if __name__ == '__main__':
    main()

# https://www.reddit.com/r/tinycode/comments/19ecwd1/i_call_it_schwarz_code_linked_in_comments/
