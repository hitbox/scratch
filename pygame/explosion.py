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
                random.randint(0, 200), random.randint(200, 1500)
            )

        animations = [random_animate(circle) for circle in circles]
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

    def __init__(self, animations):
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

    def __init__(self, circles, styles, animations):
        self.circles = circles
        self.styles = styles
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
        for circle, style in zip(self.circles, self.styles):
            image = pygamelib.circle_surface(
                circle.radius,
                style.color,
                circle_width = style.fill_or_border,
            )
            self.screen.blit(image, image.get_rect(center=circle.center))
        pygame.display.flip()


def run(display_size):
    window = pygame.Rect((0,)*2, display_size)
    spawn = pygamelib.make_rect(window, size=(100,100), center=window.center)

    # TODO
    # - animate color to transparent
    # - animate so that there is kind of a fade to smoke
    # - center of circle should look hot like fire but the edges should begin
    #   to show burned off smoke
    # - use the star-drawing thing to make the spark
    # - make a fluffy shape drawing thing?
    n = 100
    circles = [Circle(pygamelib.random_point(spawn), 0) for _ in range(n)]
    alpha = 50
    styles = [
        Style(
            pygamelib.get_color(
                random.choice(list(pygamelib.UNIQUE_THECOLORS)),
                a = alpha,
            ),
            fill_or_border = 0
        )
        for _ in circles
    ]
    animation_generator = AnimationGenerator(window)
    animation_manager = AnimationManager(animation_generator(circles))
    state = Demo(circles, styles, animation_manager)

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
