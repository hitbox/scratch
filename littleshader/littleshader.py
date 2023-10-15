import abc
import argparse
import contextlib
import math
import os
import random
import string
import time

from collections import deque
from decimal import Decimal
from itertools import groupby
from itertools import product

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

MATH_CONTEXT = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
BASE_CONTEXT = dict(
    Decimal = Decimal,
    random = random.random,
    **MATH_CONTEXT
)

EXAMPLES = [
    'sin(t)',
    'sin(y/8+t)',
    #'sin(t - dist(graph_center, (x,y)))',
    'sin(t-sqrt(x*x+y*y))',
    'sin(t+i)',
]

class EventMixin:
    """
    Mixin method to dispatch to event handler by name.
    """

    def on_event(self, event):
        eventname = pygame.event.event_name(event.type)
        handlername = f'on_{eventname.lower()}'
        handler = getattr(self, handlername, None)
        if handler:
            handler(event)


class SceneBase(abc.ABC):

    @abc.abstractmethod
    def on_event(self, event):
        ...

    @abc.abstractmethod
    def update(self):
        ...


class ShaderScene(EventMixin, SceneBase):

    def __init__(self, expressions, step):
        assert expressions
        self.expressions = expressions
        self.expression_index = 0
        self.expression = self.expressions[self.expression_index]
        self.step = step
        #
        self.clock = pygame.time.Clock()
        self.frames_per_second = 60
        self.color1 = pygame.Color('darkgray')
        self.color2 = pygame.Color('indianred')
        self.background_color = 'gray6'
        self.gui_font = pygame.font.SysFont('monospace', 20)
        self.gui_small_font = pygame.font.SysFont('monospace', 10)
        self.reset()

    def reset(self):
        self.window = pygame.display.get_surface()
        self.frame = self.window.get_rect()
        self.graph = self.frame.inflate(-self.frame.width/3, -self.frame.height/3)
        self.positions = list(
            gridpositions(
                self.graph,
                self.graph.width / self.step,
                self.graph.height / self.step,
            )
        )
        self.radius_a = 0
        self.radius_b = (min(self.graph.size) / self.step) / 2
        self.elapsed = 0

    def on_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            post_quit()
        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            # prev/next expression
            pass

    def update(self):
        frame_elapsed = self.clock.tick(self.frames_per_second)
        self.elapsed += frame_elapsed
        self.draw()

    def draw(self):
        self.window.fill(self.background_color)
        t = self.elapsed / 1000
        if self.expression:
            self.draw_circles(t)
        self.draw_gui(t)
        pygame.display.flip()

    def draw_circles(self, t):
        for i, (x, y) in enumerate(self.positions):
            radius = calc(self.expression, i, t, x, y)
            radius = remap(radius, -1, +1, self.radius_a, self.radius_b)
            color = self.color1 if math.sin(t) < 0 else self.color2
            pos = (self.graph.x + x, self.graph.y + y)
            pygame.draw.circle(self.window, color, pos, radius)
            radius_image = self.gui_small_font.render(f'{radius:0.2f}', True, 'white')
            self.window.blit(radius_image, radius_image.get_rect(center=pos))

    def draw_gui(self, t):

        def _render(string):
            return self.gui_font.render(string, True, 'azure')

        t_image = _render(f'{t=:0.2f}')
        self.window.blit(
            t_image,
            t_image.get_rect(
                topright = self.frame.topright,
            ),
        )

        expression_image = _render(str(self.expression))
        self.window.blit(
            expression_image,
            expression_image.get_rect(
                midtop = self.frame.midtop,
            )
        )


def post_quit():
    pygame.event.post(pygame.event.Event(pygame.QUIT))

def get_font(size, *sysfonts, fallback=None):
    for font in sysfonts:
        try:
            return pygame.font.SysFont(font, size)
        except FileNotFoundError:
            continue
    return pygame.fon.SysFont(fallback, size)

def lerp(a, b, t):
    return a * (1 - t) + b * t

def invlerp(a, b, x):
    return (x - a) / (b - a)

def remap(x, a, b, c, d):
    return x * (d-c) / (b-a) + c-a * (d-c) / (b-a)
    return lerp(c, d, invlerp(a, b, x))

def gridpositions(rect, xstep, ystep):
    xrange = range(rect.left, rect.width, int(xstep))
    yrange = range(rect.top, rect.height, int(ystep))
    return product(xrange, yrange)

def calc(expr, i, t, x, y, **extra_context):
    context = locals()
    del context['expr']
    context.update(BASE_CONTEXT)
    return eval(expr, context)

def sizetype(string):
    result = tuple(map(int, string.replace(',', ' ').split()))
    if len(result) < 2:
        result *= 2
    return result

def run(scene):
    """
    """
    assert isinstance(scene, SceneBase)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                scene.on_event(event)
        scene.update()

def main(argv=None):
    """
    """
    # https://tixy.land/
    parser = argparse.ArgumentParser(
        description = main.__doc__,
    )
    parser.add_argument('--expr', help='Expression to render.')
    parser.add_argument('--export')
    parser.add_argument('--size', type=sizetype, default='1024')
    parser.add_argument('--step', type=int, default=20)
    args = parser.parse_args(argv)

    expressions = [args.expr] if args.expr else EXAMPLES

    pygame.display.set_mode(args.size)
    pygame.font.init()

    shader_scene = ShaderScene(expressions, args.step)
    run(shader_scene)

    return

    loop(
        expressions,
        export_frames_path = args.export,
        size = args.size,
    )

if __name__ == '__main__':
    main()
