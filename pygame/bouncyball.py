import math
import time

import pygamelib

from pygamelib import pygame

class BouncyBall(pygamelib.DemoBase):

    def __init__(self, font, variables, steps, ranges):
        self.font = font
        self.variables = variables
        self.steps = steps
        self.ranges = ranges
        self.reset_stats()

    def reset_stats(self):
        self.stats = dict(y=dict(min=+math.inf, max=-math.inf))

    def start(self, engine):
        super().start(engine)
        self.time = 0

    def update(self):
        super().update()
        self.time += self.elapsed

        pressed = pygame.key.get_pressed()
        for key in self.variables:
            const_name = f'K_{key}'
            const = getattr(pygame, const_name)
            if pressed[const]:
                mods = pygame.key.get_mods()
                delta = self.steps.get(key, 1)
                if mods & pygame.KMOD_SHIFT:
                    delta *= -1

                minval, maxval = self.ranges.get(key, (-math.inf, math.inf))
                if minval <= self.variables[key] + delta <= maxval:
                    self.variables[key] += delta
                    self.reset_stats()

        pygamelib.post_videoexpose()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')

        a = self.variables['a']
        h = self.variables['h']
        k = self.variables['k']

        y = a * ((self.time+h) % (2*h) - h) ** 2 + k
        pos = (self.window.centerx, y)
        pygame.draw.circle(self.screen, 'brown', pos, 20, 0)

        ctx = locals()
        for key, statdict in self.stats.items():
            if key in ctx:
                val = ctx[key]
                statdict['min'] = min(val, statdict['min'])
                statdict['max'] = max(val, statdict['max'])

        lines = [
            'press variable name to increase',
            'plus shift to decrease',
            f'{y=:.0f}',
            f'time={self.time}',
        ]
        for extra in [self.variables, self.stats]:
            lines.extend(f'{key}={val}' for key, val in extra.items())

        images, rects = pygamelib.make_blitables_from_font(lines, self.font, 'azure')
        for image, rect in zip(images, rects):
            self.screen.blit(image, rect)

        pygame.display.flip()


def run(display_size):
    font = pygamelib.monospace_font(20)

    # x vertex, half of total bounce duration
    h = 575
    # y vertex, total bounce height
    k = 160
    k = 300
    variables = dict(h=h, k=k)
    # coefficient: -.000483932
    variables['a'] = 4 * k / (2*h) ** 2
    steps = {'a': 0.00001}
    ranges = dict(
        h = (1, math.inf), # avoid module division by zero
    )
    state = BouncyBall(font, variables, steps, ranges)
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
# https://sparkbox.github.io/bouncy-ball/#vanilla-js
# https://www.desmos.com/calculator/i6yunccp7v
