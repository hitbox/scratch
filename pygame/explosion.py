import random

import pygamelib

from pygamelib import pygame

class AnimationGenerator:

    def __init__(self, window):
        self.window = window

    def __call__(self, circles):
        winquads = list(map(pygame.Rect, pygamelib.rectquadrants(self.window)))
        quadwidth = winquads[0].width
        radius_a = quadwidth // 128
        radius_b = quadwidth // 2

        def random_animate(circle):
            return Animate(
                circle,
                'radius',
                0, random.randint(radius_a, radius_b),
                random.randint(0, 200), random.randint(300, 500)
            )

        animations = [
            random_animate(circles[0]),
            random_animate(circles[1]),
            random_animate(circles[2]),
            random_animate(circles[3]),
        ]
        return animations


class Animate:

    def __init__(self, obj, attr, a, b, time1, time2):
        self.obj = obj
        self.attr = attr
        self.a = a
        self.b = b
        self.time1 = time1
        self.time2 = time2

    def mix(self, time):
        return pygamelib.mix(time, self.a, self.b)

    def update(self, time):
        if self.time1 <= time <= self.time2:
            p = (time - self.time1) / (self.time2 - self.time1)
            value = self.mix(p)
            setattr(self.obj, self.attr, value)


class AnimationManager:

    def __init__(self, animations=None):
        if animations is None:
            animations = []
        self.animations = animations

    def update(self, time):
        for animation in self.animations:
            animation.update(time)


class Style:

    def __init__(self, color, fill_or_border):
        self.color = color
        self.fill_or_border = fill_or_border


class Circle:

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def __iter__(self):
        return iter((self.center, self.radius))


class Demo(pygamelib.DemoBase):

    def __init__(self, circles, style, animations):
        self.circles = circles
        self.style = style
        self.animations = animations
        self.time = 0

    def update(self):
        super().update()
        self.time += self.elapsed
        self.animations.update(self.time)
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
        for circle in self.circles:
            pygame.draw.circle(
                self.screen,
                self.style.color,
                *circle,
                self.style.fill_or_border,
            )
        pygame.display.flip()


def run(display_size):
    window = pygame.Rect((0,)*2, display_size)
    winquads = list(map(pygame.Rect, pygamelib.rectquadrants(window)))

    circles = [
        Circle(winquads[0].center, 0),
        Circle(winquads[1].center, 0),
        Circle(winquads[2].center, 0),
        Circle(winquads[3].center, 0),
    ]

    animation_generator = AnimationGenerator(window)

    animation_manager = AnimationManager(animation_generator(circles))
    style = Style('red', fill_or_border=0)

    state = Demo(circles, style, animation_manager)

    pygame.display.set_mode(display_size)
    engine = pygamelib.Engine()
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args.display_size)

if __name__ == '__main__':
    main()

# 2024-02-03 Sat.
# - wanted to make an explosion effect from circles and colors
