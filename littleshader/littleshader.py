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

EXAMPLES = [
    '1/(step/2)*math.tan(t/step*i*math.tan(index-i))', # dialogue with an alien
    '-.4/(math.hypot(i-t%10,j-t%8)-t%2*9)', # fireworks FIXME
    'math.sin(i/2) - math.sin(i-t) - j+step/2', # waves FIXME
    'math.cos(t + index + i * j)', # animated smooth noise
    'random.random() * 2 - 1',
    'j - i', # simple triangle FIXME
    'math.sin(t-math.dist((t % step, t % step),(i,j)))', # dist from shifting index
    'math.sin(t-math.sqrt(i*i+j*j))', # 1
    'math.sin(t-math.dist((0,0),(i,j)))', # 1
    'math.sin(t-math.dist((step,step),(i,j)))', # opposite of 1
    'math.sin(j/8+t)',
    'math.sin(t)',
    'math.sin(t-math.sqrt((i-7.5)**2+(j-6)**2))',
    'math.cos(t)',
    'math.sin(t+i)',
    'math.sin(t+j)',
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

    def __init__(self, expressions, step, draw_as, move_radius=0):
        assert expressions
        self.expressions = expressions
        self.expression_index = 0
        self.expression = self.expressions[self.expression_index]
        self.step = step
        assert draw_as in ('circle', 'rect')
        self.draw_as = getattr(self, f'draw_radius_as_{draw_as}')
        self.move_radius = move_radius
        #
        self.clock = pygame.time.Clock()
        self.frames_per_second = 60
        self.color1 = pygame.Color('darkgray')
        self.color2 = pygame.Color('indianred')
        self.background_color = 'gray6'

        self.gui_font = pygame.font.SysFont('monospace', 20)
        self.gui_big_font = pygame.font.SysFont('monospace', 30)
        self.gui_small_font = pygame.font.SysFont('monospace', 10)
        self.gui_color = 'azure'

        self.reset()

    def reset(self):
        self.window = pygame.display.get_surface()
        self.frame = self.window.get_rect()
        self.graph = self.frame.inflate(-self.frame.width/2, -self.frame.height/2)
        self.radius_a = 0
        self.radius_b = (min(self.graph.size) / self.step) / 2

    def on_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            post_quit()
        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            # prev/next expression
            if event.key == pygame.K_LEFT:
                di = -1
            else:
                di = +1
            self.expression_index = (self.expression_index + di) % len(self.expressions)
            self.expression = self.expressions[self.expression_index]

    def update(self):
        self.clock.tick(self.frames_per_second)
        self.draw()

    def draw(self):
        self.window.fill(self.background_color)
        t = time.time()
        if self.move_radius:
            # spin whole graph around center
            self.graph.centerx = self.frame.centerx + math.cos(t) * self.move_radius
            self.graph.centery = self.frame.centery + math.sin(t) * self.move_radius
        if self.expression:
            self.draw_expression(t)
        self.draw_gui(t)
        pygame.display.flip()

    def _render(self, string):
        return self.gui_font.render(string, True, self.gui_color)

    def _render_small(self, string):
        return self.gui_small_font.render(string, True, self.gui_color)

    def _render_big(self, string):
        return self.gui_big_font.render(string, True, self.gui_color)

    def draw_expression(self, t):
        step = self.step
        ystep = int(self.graph.height / step)
        yitems = enumerate(range(self.graph.top, self.graph.bottom, ystep))
        index = 0
        for j, y in yitems:
            xstep = int(self.graph.width / step)
            xitems = enumerate(range(self.graph.left, self.graph.right, xstep))
            for i, x in xitems:
                radius = eval(self.expression, globals(), locals())
                color = self.color1 if radius < 0 else self.color2
                radius = remap(abs(radius), 0, +1, self.radius_a, self.radius_b)
                self.draw_as(radius, x, y, color)
                index += 1

    def draw_radius_as_circle(self, radius, x, y, color):
        pygame.draw.circle(self.window, color, (x, y), radius)

    def draw_radius_as_rect(self, radius, x, y, color):
        side = radius * 2
        rect = pygame.Rect(0, 0, side, side)
        rect.center = (x, y)
        pygame.draw.rect(self.window, color, rect)

    def draw_gui(self, t):
        t_image = self._render(f'{t=:0.2f}')
        self.window.blit(
            t_image,
            t_image.get_rect(
                bottomleft = self.frame.bottomleft,
            ),
        )

        expression_image = self._render_big(str(self.expression))
        self.window.blit(
            expression_image,
            expression_image.get_rect(
                midtop = self.frame.midtop,
            )
        )

        fps_image = self._render(f'{self.clock.get_fps():.2f}')
        self.window.blit(
            fps_image,
            fps_image.get_rect(
                bottomright = self.frame.bottomright,
            )
        )


def post_quit():
    pygame.event.post(pygame.event.Event(pygame.QUIT))

def lerp(a, b, t):
    return a * (1 - t) + b * t

def invlerp(a, b, x):
    return (x - a) / (b - a)

def remap(x, a, b, c, d):
    return x * (d-c) / (b-a) + c-a * (d-c) / (b-a)
    return lerp(c, d, invlerp(a, b, x))

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
    parser.add_argument('--size', type=sizetype, default='1024')
    parser.add_argument('--step', type=int, default=20)
    parser.add_argument('--draw-as', choices=['circle', 'rect'], default='rect')
    args = parser.parse_args(argv)

    expressions = [args.expr] if args.expr else EXAMPLES

    pygame.display.set_mode(args.size)
    pygame.font.init()

    shader_scene = ShaderScene(expressions, args.step, args.draw_as)
    run(shader_scene)

if __name__ == '__main__':
    main()
