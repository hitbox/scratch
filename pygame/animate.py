import argparse

from types import SimpleNamespace
from xml.etree import ElementTree

import pygamelib

from pygamelib import pygame

# NOTES
# - want objects that have any amount of attributes for dimensions and styling
#   and such
# - want to animate those attributes
# - want to ignore missing attributes

class Circle(SimpleNamespace):

    @classmethod
    def from_attrib(cls, **kwargs):
        kwargs['cx'] = int(kwargs.get('cx', '0'))
        kwargs['cy'] = int(kwargs.get('cy', '0'))
        kwargs['r'] = int(kwargs.get('r', '0'))
        return cls(**kwargs)

    def draw(self, surf, color, width, offset):
        x, y = offset + (self.cx, self.cy)
        return pygame.draw.circle(surf, color, (x, y), self.r, width)


class Rect(SimpleNamespace):

    @classmethod
    def from_attrib(cls, **kwargs):
        kwargs['x'] = int(kwargs.get('x', '0'))
        kwargs['y'] = int(kwargs.get('y', '0'))
        kwargs['w'] = int(kwargs.get('w', '0'))
        kwargs['h'] = int(kwargs.get('h', '0'))
        return cls(**kwargs)

    def draw(self, surf, color, width, offset):
        x, y = offset + (self.x, self.y)
        return pygame.draw.rect(surf, color, (x, y, self.w, self.h), width)


class Polygon(SimpleNamespace):

    @classmethod
    def from_attrib(cls, **kwargs):
        kwargs['points'] = [
            int_tuple(tuple_string.split(',')) for tuple_string in kwargs['points'].split()
        ]
        return cls(**kwargs)

    def draw(self, surf, color, width, offset):
        points = [offset + point for point in self.points]
        return pygame.draw.polygon(surf, color, points, width)


class typed_container:

    def __init__(self, container, type_):
        self.container = container
        self.type_ = type_

    def __call__(self, iterable):
        return self.container(map(self.type_, iterable))


def splitarg(string):
    return string.replace(',', ' ').split()

def shape_type(string):
    shape, id_, color, *remaining = splitarg(string)
    if shape == 'rect':
        # NOTE
        # - wrapped in tuple
        remaining = (Rect(tuple(map(int, remaining))), )
    elif shape == 'circle':
        if len(remaining) == 2:
            center, radius = remaining
        elif len(remaining) == 3:
            cx, cy, radius = remaining
            center = (cx, cy)
        center = tuple(map(int, center))
        radius = int(radius)
        remaining = (Circle(center, radius),)
    else:
        raise ValueError
    shapefunc = getattr(pygame.draw, shape)
    return (shapefunc, id_, color, *remaining)

def animate_type(string):
    id_, attr, *remaining = splitarg(string)
    if attr == 'center':
        cx1, cy1, cx2, cy2, start, end = map(int, remaining)
        remaining = ((cx1, cy1), (cx2, cy2), start, end)
    elif attr == 'size':
        w1, h1, w2, h2, start, end = map(int, remaining)
        remaining = ((w1, h1), (w2, h2), start, end)
    elif attr == 'color':
        color1, color2 = map(pygame.Color, remaining[:2])
        start, end = map(int, remaining[2:])
        remaining = (color1, color2, start, end)
    elif attr == 'radius':
        remaining = map(int, remaining)
    else:
        raise ValueError
    return (id_, attr, *remaining)

int_tuple = typed_container(tuple, int)

tag2class = {
    'circle': Circle,
    'polygon': Polygon,
    'rect': Rect,
}

def shapes_from_xml(shapes):
    for element in shapes:
        class_ = tag2class[element.tag]
        instance = class_.from_attrib(**element.attrib)
        yield instance

def save_animation_code():
        for animation in animations:
            id_, attr, value1, value2, time1, time2 = animation
            if time1 <= time <= time2:
                shapefunc, color, shape = shapes[id_]
                mixtime = (time - time1) / (time2 - time1)
                if isinstance(value1, (int, float)):
                    value = pygamelib.mix(mixtime, value1, value2)
                else:
                    value = pygamelib.mixiters(mixtime, value1, value2)
                if attr == 'color':
                    shapes[id_] = (shapefunc, pygame.Color(value), shape)
                else:
                    setattr(shape, attr, value)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'xml',
        type = argparse.FileType(),
    )
    args = parser.parse_args(argv)

    tree = ElementTree.parse(args.xml)
    root = tree.getroot()

    engine_element = root.find('engine')
    if engine_element:
        offset = int_tuple(engine_element.find('offset').attrib.values())
    offset = pygame.Vector2(offset)

    shapes = list()
    for shapes_element in root.findall('shapes'):
        shapes.extend(shapes_from_xml(shapes_element))

    framerate = args.framerate
    clock = pygame.time.Clock()

    running = True
    time = 0
    screen = pygame.display.set_mode(args.display_size)
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
        # draw
        screen.fill('black')
        for shape in shapes:
            shape.draw(screen, 'magenta', 1, offset)
        pygame.display.flip()
        #
        elapsed = clock.tick(framerate)
        time += elapsed

if __name__ == '__main__':
    main()
