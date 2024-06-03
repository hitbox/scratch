import argparse
import contextlib
import itertools as it
import math
import os
import turtle
import unittest

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class TestLSystem(unittest.TestCase):

    def test_koch_right_angles(self):
        generator = koch_right_angles()
        self.assertEqual(generator(0), 'F')
        self.assertEqual(generator(1), 'F+F-F-F+F')
        self.assertEqual(
            generator(2),
            'F+F-F-F+F+F+F-F-F+F-F+F-F-F+F-F+F-F-F+F+F+F-F-F+F'
        )


class LSystem:

    def __init__(self, axiom, rules):
        self.axiom = axiom
        self.rules = rules

    def __call__(self, iterations):
        """
        Expand the axiom n iterations using the system rules.
        """
        current_string = self.axiom
        for _ in range(iterations):
            next_string = []
            for char in current_string:
                next_string.append(self.rules.get(char, char))
            current_string = ''.join(next_string)
        return current_string


class KochSnowflake:

    def __init__(self, left, right, forward):
        self.left = left
        self.right = right
        self.forward = forward

    def subloop(self, length, i=1):
        if i == 0:
            self.forward(length)
        else:
            self.subloop(length/3, i-1)
            self.left(60)
            self.subloop(length/3, i-1)
            self.right(120)
            self.subloop(length/3, i-1)
            self.left(60)
            self.subloop(length/3, i-1)

    def loop(self, length):
        for i in range(3):
            self.subloop(length, i=3)
            self.right(120)


class Cursor:

    def __init__(self, turn_angle, length=1, position=(0,0), angle=0):
        self.turn_angle = turn_angle
        self.length = length
        self.position = pygame.Vector2(position)
        self.angle = angle

    def left(self):
        self.angle += -self.turn_angle

    def right(self):
        self.angle += self.turn_angle

    def forward(self, length):
        # angle in degrees for from_polar
        other = pygame.Vector2.from_polar((length, self.angle))
        self.position += other
        return self.position

    def forward_one(self):
        return self.forward(self.length)


class CursorMapping:

    def __init__(self, rule_actions):
        self.rule_actions = rule_actions

    def __call__(self, symbol, obj):
        """
        Call the action for given symbol.
        """
        name = self.rule_actions[symbol]
        if name:
            method = getattr(obj, name)
            return method()


class PointGenerator:

    def __init__(self, symbols, cursor_mapping, cursor):
        self.symbols = symbols
        self.cursor_mapping = cursor_mapping
        self.cursor = cursor

    def __iter__(self):
        return self

    def __next__(self):
        symbol = next(self.symbols)
        pos = self.cursor_mapping(symbol, self.cursor)
        return pos


def wrap_points(points):
    xs, ys = zip(*points)
    left = min(xs)
    top = min(ys)
    right = max(xs)
    bottom = max(ys)
    width = right - left
    height = bottom - top
    return pygame.Rect(left, top, width, height)

def wrap_rects(rects):
    return pygame.Rect((0,)*4).unionall(rects)

def lerp(time, a, b):
    """
    Return the value between a and b at time.
    """
    return a * (1 - time) + b * time

def remap(x, a, b, c, d):
    """
    Return x from range a and b to range c and d.
    """
    return x*(d-c)/(b-a) + c-a*(d-c)/(b-a)

def run_turtle():
    turtle.color('red')
    koch_snowflake = KochSnowflake(turtle.left, turtle.right, turtle.forward)
    koch_snowflake.loop(500)

def run_pygame():
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    frame = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 60
    font = pygame.font.SysFont('monospace', 20)

    cursor = Cursor()
    koch_snowflake = KochSnowflake(cursor.left, cursor.right, cursor.forward)
    koch_snowflake.loop(300)
    cursor.points.append(cursor.points[0].copy())

    # center the snow flake
    points_wrapped = wrap_points(cursor.points)
    delta = pygame.Vector2(frame.center) - points_wrapped.center
    for point in cursor.points:
        point += delta

    n = 0
    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        # update
        # NOTE
        # - n is a length not an index, so don't "wrap" until +1
        n = (n + 1) % (len(cursor.points) + 1)

        # draw
        screen.fill('black')
        points = cursor.points[:n]
        if len(points) > 1:
            pygame.draw.lines(screen, 'azure', False, points)

        lines = [
            'Escape/Q to quit',
            f'{clock.get_fps():.2f} FPS',
        ]
        images = [font.render(line, True, 'azure') for line in lines]
        rects = [image.get_rect() for image in images]
        for r1, r2 in zip(rects, rects[1:]):
            r2.topright = r1.bottomright
        wrapped = wrap_rects(rects)
        delta = pygame.Vector2(frame.bottomright) - wrapped.bottomright
        for rect in rects:
            rect.topleft += delta
        for image, rect in zip(images, rects):
            screen.blit(image, rect)

        pygame.display.flip()

def original_main(argv=None):
    """
    Draw the Koch snowflake with turtle or pygame.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['turtle', 'pygame'])
    args = parser.parse_args(argv)
    if args.command == 'turtle':
        run_turtle()
    elif args.command == 'pygame':
        run_pygame()

def render_lines(font, lines, color, antialias=True):
    images = [font.render(line, antialias, color) for line in lines]
    rects = [image.get_rect() for image in images]
    for r1, r2 in it.pairwise(rects):
        r2.topleft = r1.bottomleft
    return (images, rects)

def run_engine(points_generator):
    points_generator = iter(points_generator)
    points = [pygame.Vector2()]
    while True:
        pos = next(points_generator)
        if pos:
            points.append(pos.copy())
            break
    target = None
    complete = False
    new_point_bucket = 0
    new_point_every = 30

    pygame.font.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((1000,)*2)
    window = screen.get_rect()
    font = pygame.font.SysFont('monospace', 20)
    closed = False
    offset = pygame.Vector2(window.center)
    running = True
    elapsed = 0
    dragged = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    offset += event.rel
                    dragged = True
        window_center = pygame.Vector2(window.center)
        head_screen = points[-1] + offset
        distance = window_center.distance_to(head_screen)
        if not complete:
            if target:
                # animating new point towards destination
                if points[-1].distance_to(target) < 1:
                    points[-1].update(target)
                    target = None
                else:
                    points[-1].move_towards_ip(target, 0.5)
            else:
                if (new_point_bucket + elapsed) < new_point_every:
                    new_point_bucket += elapsed
                else:
                    new_point_bucket = (new_point_bucket + elapsed) % new_point_every
                    try:
                        target = next(points_generator)
                    except StopIteration:
                        complete = True
                    else:
                        points.append(pygame.Vector2(points[-1]))

            # auto center while not complete
            t = remap(distance, 20, 300, 0.05, 1)
            offset.move_towards_ip(window_center - points[-1], t)
        elif not dragged:
            wrapped = wrap_points(points)
            world_center = wrapped.center
            center_distance = window_center.distance_to(world_center)
            t = remap(center_distance, 0, 300, 0, 1)
            offset.move_towards_ip(window_center - world_center, t)
        # draw
        screen.fill('black')
        _points = [p + offset for p in points]
        if target:
            pygame.draw.lines(screen, 'white', closed, _points[:-1])
            pygame.draw.line(screen, 'purple', _points[-2], _points[-1])
        else:
            pygame.draw.lines(screen, 'white', closed, _points)
        for p in _points:
            pygame.draw.circle(screen, 'brown', p, 2)
        elapsed = clock.tick()
        lines = [
            f'fps={clock.get_fps():0.0f}',
            f'{offset=}',
            f'{distance=:0.2f}',
            f'{points[-1]=}',
        ]
        screen.blits(list(zip(*render_lines(font, lines, 'white'))))
        pygame.display.update()

def snowflake(iterations, length):
    # https://en.wikipedia.org/wiki/Koch_snowflake#Representation_as_Lindenmayer_system
    generator = LSystem(
        axiom = 'F',
        rules = {
            'F': 'F+F--F+F',
        },
    )
    sequence = generator(iterations)
    cursor_mapping = CursorMapping({
        'F': 'forward_one',
        '+': 'left',
        '-': 'right',
    })
    cursor = Cursor(turn_angle=60, length=length)
    symbols = iter(sequence)
    points_generator = PointGenerator(symbols, cursor_mapping, cursor)
    return points_generator

def gosper(iterations, length):
    # https://en.wikipedia.org/wiki/Gosper_curve#Lindenmayer_system
    generator = LSystem(
        axiom = 'A',
        rules = {
            'A': 'A-B--B+A++AA+B-',
            'B': '+A-BB--B-A++A+B',
            # 'A', 'B' -> move forward
            # '+' -> turn left 60 deg.
            # '-' -> turn right 60 deg.
        },
    )
    sequence = generator(iterations)
    cursor_mapping = CursorMapping({
        'A': 'forward_one',
        'B': 'forward_one',
        '+': 'left',
        '-': 'right',
    })
    cursor = Cursor(turn_angle=60, length=length)
    symbols = iter(sequence)
    points_generator = PointGenerator(symbols, cursor_mapping, cursor)
    return points_generator

def moore(iterations, length):
    # https://en.wikipedia.org/wiki/Moore_curve#Representation_as_Lindenmayer_system
    generator = LSystem(
        axiom = 'LFL+F+LFL',
        rules = {
            'L': '-RF+LFL+FR-',
            'R': '+LF-RFR-FL+',
        },
    )
    sequence = generator(iterations)
    cursor_mapping = CursorMapping({
        'F': 'forward_one',
        'L': None,
        'R': None,
        '+': 'right',
        '-': 'left',
    })
    cursor = Cursor(turn_angle=90, length=length)
    symbols = iter(sequence)
    points_generator = PointGenerator(symbols, cursor_mapping, cursor)
    return points_generator

def simple_star(iterations, length):
    # https://susam.net/fd-100.html
    # simple star shape
    generator = LSystem(
        axiom = 'A',
        rules = {
            'A': 'FRA',
        },
    )
    sequence = generator(iterations)
    cursor_mapping = CursorMapping({
        'F': 'forward_one',
        'R': 'right',
        'A': None,
    })
    cursor = Cursor(turn_angle=144, length=length)
    symbols = iter(sequence)
    points_generator = PointGenerator(symbols, cursor_mapping, cursor)
    return points_generator

CURVES = {
    'snowflake': snowflake,
    'gosper': gosper,
    'moore': moore,
    'simple_star': simple_star,
}

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'curve',
        choices = list(CURVES),
    )
    parser.add_argument('iterations', type=int, default=0)
    parser.add_argument('--line', type=int, default=1)
    args = parser.parse_args(argv)

    curve = eval(args.curve)
    run_engine(curve(args.iterations, args.line))

if __name__ == '__main__':
    main()

# 2023-11-06
# https://compileralchemy.substack.com/p/cursing-and-re-cursing-what-if-we
# https://en.wikipedia.org/wiki/Weierstrass_function
# 2024-06-02 Sun.
# https://en.wikipedia.org/wiki/Koch_snowflake
# "Paged Out! #4" page 28 "Generate ASCII-Root-Art using formal grammar and randomness"
# https://pagedout.institute/?page=issues.php
