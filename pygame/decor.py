import math

import pygamelib

from pygamelib import pygame

class Pen:

    def __init__(self, position=None, angle=None):
        if position is None:
            position = (0,0)
        self.position = pygame.Vector2(position)
        if angle is None:
            angle = 0
        self.angle = angle

    def copy(self):
        return self.position.copy()

    def move(self, length):
        radians = math.radians(self.angle)
        direction = pygame.Vector2(
            math.cos(radians),
            -math.sin(radians)
        )
        direction *= length
        self.position += direction

    def turn(self, angle):
        self.angle = (self.angle + angle) % 360

    def right(self):
        self.turn(-90)

    def left(self):
        self.turn(90)


def corner_border(pen, rect, portion):
    horizontal, vertical = rect.size
    for side_length in [horizontal, vertical, horizontal, vertical]:
        # starting in a corner
        p1 = pen.copy()

        pen.move(side_length * portion)
        p2 = pen.copy()
        yield (p1, p2)

        # skip
        pen.move(side_length - portion * side_length * 2)

        p1 = pen.copy()
        pen.move(side_length * portion)
        p2 = pen.copy()
        yield (p1, p2)

        pen.right()

def inner_corner_border(pen, rect, portion):
    # inverted brackets around a rect's corners
    horizontal, vertical = rect.size

    # starting topleft facing right
    pen.move(horizontal * portion)
    for side in [horizontal, vertical, horizontal, vertical]:
        p1 = pen.copy()
        pen.move(side - portion * side * 2)
        p2 = pen.copy()
        yield (p1, p2)

        p1 = pen.copy()
        pen.right()
        pen.move(side * portion)
        p2 = pen.copy()
        yield (p1, p2)

        pen.left()
        pen.move(side * portion)
        p3 = pen.copy()
        yield (p2, p3)

        pen.right()

def main(argv=None):
    """
    Draw decorations from basic shapes.
    """
    parser = pygamelib.command_line_parser(
        description = main.__doc__,
    )
    args = parser.parse_args(argv)

    window = pygame.Rect(0, 0, *args.display_size)
    shrink = 0.50
    rect = window.inflate(-shrink * window.width, -shrink * window.height)

    horizontal = rect.width - 1
    vertical = rect.height - 1

    pen = Pen(position=rect.topleft)
    portion = 0.40

    # TODO
    # - interactively create lines

    lines = list(inner_corner_border(pen, rect, portion))

    colors = (
        'red',
        'green',
        'blue',
        'brown',
        'purple',
        'orange',
        'teal',
        'indigo',
        'yellow',
        'olive',
        'fuchsia',
        'navy',
    )

    screen = pygame.display.set_mode(window.size)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill('black')
        pygame.draw.rect(screen, 'grey10', rect, 1)
        for (p1, p2), color in zip(lines, colors):
            pygame.draw.line(screen, color, p1, p2)
        pygame.display.flip()

if __name__ == '__main__':
    main()
