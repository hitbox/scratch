import math
import time

import pygamelib

from pygamelib import pygame

class Dweet(pygamelib.DemoBase):

    def __init__(self, func):
        self.func = func

    def reset_stats(self):
        self.stats = dict(y=dict(min=+math.inf, max=-math.inf))

    def start(self, engine):
        super().start(engine)
        self.time = 0

    def update(self):
        super().update()
        self.time += self.elapsed
        pygamelib.post_videoexpose()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        #self.screen.fill('black')
        self.func(self.screen, self.time)
        pygame.display.flip()


def taupelink_signed_distance_functions(surf, t):
    # https://www.dwitter.net/d/29383
    # for(i=1e4; i--; x.fillRect(30*X,30*Y,(--m*m-a-b)**2>3,1) ) {
    #   X = i * t % 64,
    #   Y = X*i%36,
    #   a = (X%8-4)**2,
    #   b = (Y%8-4)**2,
    #   m = a < b ? a : b,
    #   x.fillStyle = m-- & 3 ? '#359' : '#CBA'
    t /= 1000
    i = 10_000
    while i:
        X = i * t % 64
        Y = X * i % 36
        a = (X % 8 - 4) ** 2
        b = (Y % 8 - 4) ** 2
        m = min(a, b)
        m -= 1
        if int(m) & 3:
            color = '#335599'
        else:
            color = '#CCBBAA'
        x = 30 * X
        y = 30 * Y
        m -= 1
        w = (m * m - a - b) ** 2 > 3
        pygame.draw.rect(surf, color, (x, y, w, 1))
        i -= 1

def run(display_size):
    state = Dweet(taupelink_signed_distance_functions)
    pygame.display.set_mode(display_size)
    engine = pygamelib.Engine()
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args.display_size)

if __name__ == '__main__':
    main()

# 2024-02-02 Fri.
# Dweet of the week: Signed Distance Functions by taupelink
# https://www.reddit.com/r/tinycode/comments/1ah7sxa/dweet_of_the_week_signed_distance_functions_by/
