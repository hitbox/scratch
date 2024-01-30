import argparse

from collections import deque
from collections import namedtuple

import pygamelib

from pygamelib import pygame

class BezierDemo(pygamelib.DemoBase):

    def __init__(self, path, nsamples):
        self.path = path
        self.nsamples = nsamples

    def start(self, engine):
        super().start(engine)
        self.path_index = 0
        self.path_time = 0
        self.lines = [
            path_item.point_at(t / self.nsamples)
            for path_item in self.path
            for t in range(self.nsamples)
        ]

    def update(self):
        super().update()
        self.draw()
        if self.path_time + 1 == self.nsamples:
            self.path_time = 0
            self.path_index = (self.path_index + 1) % len(self.path)
        else:
            self.path_time += 1

    def draw(self):
        path_item = self.path[self.path_index]
        t = self.path_time / self.nsamples
        point = pygame.Vector2(path_item.point_at(t))
        normal = pygame.Vector2(path_item.derivative_at(t)).rotate(90)

        self.screen.fill('black')
        pygame.draw.lines(self.screen, 'blue', False, self.lines)
        pygame.draw.circle(self.screen, 'red', point, 10)
        pygame.draw.line(self.screen, 'magenta', point, point + normal, 1)
        pygame.display.flip()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()


class move_absolute:

    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1

    def end(self):
        return self.p1

    def point_at(self, time):
        a = pygame.Vector2(self.p0)
        b = pygame.Vector2(self.p1)
        return pygamelib.mix(time, a, b)

    def derivative_at(self, time):
        return self.point_at(time)


move = namedtuple('move', 'type point')

cubic_curve = namedtuple('cubic_curve', 'type p0 p1 p2 p3')

close_path = namedtuple('close_path', '')

def trash():
    __slots__ = ()

    def end(self):
        return self.p3

    def point_at(self, time):
        return pygamelib.cubic_bezier(self.p0, self.p1, self.p2, self.p3, time)

    def derivative_at(self, time):
        return pygamelib.cubic_bezier_derivative(self.p0, self.p1, self.p2, self.p3, time)


def parse_path(string):
    path = []
    items = deque(string.split())

    def take(n):
        for _ in range(n):
            yield items.popleft()

    while items:
        command = items.popleft()
        if command in 'M':
            if path:
                start = path[-1].end()
            else:
                start = (0,)*2
            end = tuple(map(int, take(2)))
            path.append(move_absolute(start, end))
        elif command in 'C':
            if path:
                start = path[-1].end()
            else:
                start = (0,)*2
            # take two, three times
            args = (tuple(map(int, take(2))) for _ in range(3))
            path.append(cubic_curve(start, *args))
        else:
            raise NotImplementedError(command)

    return path

def tokenize(string):
    chars = iter(string)
    for char in chars:
        if char == 'M':
            # move absolute coordinates
            # TODO
            # - left off here
            # - thinking we need a tokenize step
            # - how about this yield style?
            yield move
            yield 'absolute'
        elif char == 'C':
            # absolute coordinates bezier curve
            command = [cubic_curve, 'absolute']
            number = ''
        elif char == 'c':
            # relative coordinates bezier curve
            command = [cubic_curve, 'relative']
            number = ''
        elif char in 'zZ':
            # straight line back to first point in path
            command = [close_path]


def parse_path(string):
    chars = list(chars)
    command = None
    number = None
    while chars:
        char = chars.pop()
        if char in 'CMZcz':
            # finalize last command
            # begin new command
            if char == 'M':
                # move absolute coordinates
                command = [move, 'absolute']
                number = ''
            elif char == 'C':
                # absolute coordinates bezier curve
                command = [cubic_curve, 'absolute']
                number = ''
            elif char == 'c':
                # relative coordinates bezier curve
                command = [cubic_curve, 'relative']
                number = ''
            elif char in 'zZ':
                # straight line back to first point in path
                command = [close_path]
        elif char.isdigit() or char in '+-':
            number += char

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('--samples', type=int, default=100)
    args = parser.parse_args(argv)

    path = parse_path(args.path)
    print(path)
    return

    state = BezierDemo(path, args.samples)
    engine = pygamelib.Engine()

    pygame.display.set_mode((800,)*2)

    engine.run(state)

if __name__ == '__main__':
    main()
