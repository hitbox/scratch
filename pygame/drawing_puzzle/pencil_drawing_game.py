import abc
import argparse
import contextlib
import itertools as it
import math
import operator as op
import os
import pickle
import random

from collections import deque
from itertools import pairwise
from operator import itemgetter

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

quit_event = pygame.event.Event(pygame.QUIT)

CW_RECT = ['top', 'right', 'bottom', 'left']

class GameError(Exception):
    pass


class Engine:

    def __init__(self):
        self.running = False

    def run(self, state):
        state.start(engine=self)
        self.running = True
        while self.running:
            state.update(engine=self)


class State(abc.ABC):

    @abc.abstractmethod
    def start(self, engine):
        pass

    @abc.abstractmethod
    def update(self, engine):
        pass


class GameManager(State):

    def __init__(
        self,
        *,
        screen_size,
        game,
        pencil_renderer,
        framerate = 60,
    ):
        self.screen_size = screen_size
        self.game = game
        self.pencil_renderer = pencil_renderer
        self.framerate = framerate

        self.screen = None
        self.window = None
        self.clock = None
        self.gui_font = None

    def start(self, engine):
        pygame.font.init()
        self.screen = pygame.display.set_mode(self.screen_size)
        self.window = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.gui_font = pygame.font.SysFont('monospace', 18)

    def update(self, engine):
        elapsed = self.clock.tick(self.framerate)
        self.dispatch_events(engine, pygame.event.get())
        self.game.update(engine, self, elapsed)
        self.draw(engine)

    def dispatch_events(self, engine, events):
        for event in events:
            self.dispatch_event(engine, event)

    def dispatch_event(self, engine, event):
        method = getattr(self, event_methodname(event), None)
        if method:
            method(engine, event)

    def do_quit(self, engine, event):
        engine.running = False

    def do_keydown(self, engine, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.event.post(quit_event)

    def draw(self, engine):
        self.screen.fill('black')
        # draw game area
        pygame.draw.rect(self.screen, 'magenta', self.game.gamearea, 1)
        # draw pencil
        self.pencil_renderer.draw(self.screen, self.game.pencil)
        # draw walls
        for wall in self.game.walls:
            pygame.draw.rect(self.screen, )

        # draw gui
        pygame.display.flip()


class Vector(pygame.Vector2):

    def __init__(self, *args):
        super().__init__(*args)
        self.previous = self.copy()


class Game:

    def __init__(
        self,
        *,
        gamearea,
        pencil,
        line_manager,
        walls,
    ):
        self.gamearea = gamearea
        self.pencil = pencil
        self.line_manager = line_manager
        self.walls = walls
        self.new_position = None
        self.move_line = None

    def update(self, engine, state, elapsed):
        pencil = self.pencil

        self.new_position = pencil.position + pencil.velocity
        self.move_line = (pencil.position, self.new_position - pencil.position)

        self.new_direction = self.new_position - pencil.position
        self.prev_direction = pencil.position - pencil.position.previous

        pencil.position.previous.update(pencil.position)
        pencil.position.update(self.new_position)
        pencil.rect.center = pencil.position


class LineManager:
    # NOTES
    # - motivation here is to have a way to consider the drawing points before
    #   adding them to the list of lines.
    # - if pencil touches its own line, it dies.
    # - probably need to keep lines and drawing points separate for a, say,
    #   flashing period showing a completed line like tetris.

    def __init__(self, lines):
        self.lines = lines
        self.drawing_points = []

    @classmethod
    def from_rect(cls, rect):
        return cls(rectlines(rect))


class Pencil:

    def __init__(
        self,
        position,
        speed,
        velocity,
        rect_size,
        is_drawing = False,
    ):
        self.position = position
        self.speed = speed
        self.velocity = velocity
        self.previous = self.position.copy()
        self.is_drawing = is_drawing
        self.rect = pygame.Rect((0,)*2, rect_size)
        self.rect.center = self.position

    def stop(self):
        self.velocity.update(0,0)
        self.is_drawing = False


class PencilRenderer:

    def draw(self, surf, pencil):
        pygame.draw.rect(surf, 'brown', pencil.rect, 1)
        pygame.draw.line(surf, 'red', pencil.position.previous, pencil.position)


def opposite(list_, value):
    return list_[list_.index(value) + len(list_) // 2]

def rectlines(rect):
    yield (rect.topleft, rect.topright)
    yield (rect.topright, rect.bottomright)
    yield (rect.bottomright, rect.bottomleft)
    yield (rect.bottomleft, rect.topleft)

def event_methodname(event, prefix='do_'):
    event_name = pygame.event.event_name(event.type).lower()
    return f'{prefix}{event_name}'

def slope(line):
    (x1, y1), (x2, y2) = line
    run = (x2 - x1)
    if run == 0:
        return math.inf
    rise = (y2 - y1)
    return rise / run

def clamp(x, a, b):
    if x < a:
        return a
    elif x > b:
        return b
    return x

def iter_line_points(lines):
    for (start, end) in lines:
        yield start
        yield end

def is_point_on_line(point, line):
    x, y = point
    (x1, y1), (x2, y2) = line

    # Check if the line is vertical (to avoid division by zero)
    if x1 == x2:
        return x == x1 and min(y1, y2) <= y <= max(y1, y2)

    # Calculate the slope (m) and y-intercept (c) of the line
    m = (y2 - y1) / (x2 - x1)
    c = y1 - m * x1

    # Check if the given point lies on the line
    return y == m * x + c

def is_point_on_lines(point, lines):
    return any(map(is_point_on_line, it.repeat(point), lines))

def line_intersection(line1, line2):
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2

    # Calculate the denominator
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if denominator == 0:
        # Lines are parallel, no intersection
        return

    # Calculate intersection point coordinates
    intersection_x = (
        (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
    ) / denominator
    intersection_y = (
        (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
    ) / denominator

    # Check if the intersection point lies within the line segments
    if (
        min(x1, x2) <= intersection_x <= max(x1, x2)
        and
        min(y1, y2) <= intersection_y <= max(y1, y2)
        and
        min(x3, x4) <= intersection_x <= max(x3, x4)
        and
        min(y3, y4) <= intersection_y <= max(y3, y4)
    ):
        return (intersection_x, intersection_y)

def get_rect(rect=None, **kwargs):
    if rect is None:
        rect = pygame.Rect((0,)*4)
    else:
        rect = rect.copy()
    for key, val in kwargs.items():
        setattr(rect, key, val)
    return rect

def mirror_rect(rect, around, **kwargs):
    assert around in CW_RECT
    opposite = CW_RECT[(CW_RECT.index(attrs) + 2) % len(attrs)]
    result = rect.copy()
    setattr(result, opposite, around)
    for key, val in kwargs.items():
        setattr(result, key, val)
    return result

def scaleiter(iterable, scale):
    yield from (value * scale for value in iterable)

def walls_around(rect, scale=1):
    # top
    yield get_rect(
        rect,
        width = rect.width*scale,
        midbottom = (rect.centerx, rect.top),
    )
    # right
    yield get_rect(
        rect,
        height = rect.height*scale,
        midleft = (rect.right + 1, rect.centery),
    )
    # bottom
    yield get_rect(
        rect,
        width = rect.width*scale,
        midtop = (rect.centerx, rect.bottom + 1),
    )
    # left
    yield get_rect(
        rect,
        height = rect.height*scale,
        midright = (rect.left, rect.centery),
    )

def run():
    screen_size = (800,)*2
    gamearea = get_rect(
        size = tuple(scaleiter(screen_size, 0.75)),
        center = tuple(scaleiter(screen_size, 0.5)),
    )
    pencil = Pencil(
        # start in middle left
        position = Vector(
            gamearea.left,
            gamearea.centery,
        ),
        speed = 3,
        velocity = Vector(3,0),
        rect_size = (20,)*2,
    )
    state = GameManager(
        screen_size = screen_size,
        game = Game(
            gamearea = gamearea,
            pencil = pencil,
            line_manager = LineManager.from_rect(gamearea),
            walls = list(
                walls_around(
                    gamearea,
                    scale = 2,
                )
            ),
        ),
        pencil_renderer = PencilRenderer(),
    )
    engine = Engine()
    engine.run(state)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()

# 2023-12-23
