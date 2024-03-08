import argparse
import re

from types import SimpleNamespace
from xml.etree import ElementTree

import pygamelib

from pygamelib import pygame

class Style(SimpleNamespace):
    pass


class Animate:

    @classmethod
    def from_attrib(cls, **attrib):
        # XXX: Thinking
        # - get type from object attribute?
        # - what if it can be several types?
        # - explicit type converter
        # - but allow just about anything?

        kwargs = {fixkey(key): int(value) for key, value in attrib.items()}

        kwargs.setdefault('obj', None)
        # default to value from object
        kwargs.setdefault('from_', getattr(obj, attrib['attribute']))

        if 'dur' in attrib:
            dur = int(kwargs.pop('dur'))
            kwargs.setdefault('end', dur - kwargs.get('start', 0))

        return cls(**kwargs)

    def update(self, time):
        if not hasattr(self, 'obj'):
            return

        if hasattr(self, 'start') and hasattr(self, 'end'):
            self.update_absolute(time)
        elif hasattr(self, 'dur'):
            pass

    def update_absolute(self, time):
        if self.start <= time <= self.end:
            mixtime = (time - self.start) / (self.end - self.start)
            value = pygamelib.mix(mixtime, self.from_, self.to)
            setattr(self.obj, self.attribute, value)


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


class Lines(SimpleNamespace):

    @classmethod
    def from_attrib(cls, **kwargs):
        kwargs['closed'] = int(kwargs.get('closed', '0'))
        kwargs['points'] = [
            int_tuple(tuple_string.split(',')) for tuple_string in kwargs['points'].split()
        ]
        return cls(**kwargs)

    def draw(self, surf, color, width, offset):
        points = [offset + point for point in self.points]
        return pygame.draw.lines(surf, color, self.closed, points, width)


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


def fixkey(name):
    if name == 'from':
        name = 'from_'
    return name

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
    'lines': Lines,
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

def walk_elements(root, parents=None):
    if parents is None:
        parents = []
    yield (root, parents)
    for child in root:
        yield from walk_elements(child, parents=parents + [root])

def system_from_xml(xml):
    tree = ElementTree.parse(xml)
    root = tree.getroot()

    engine_element = root.find('engine')
    if engine_element:
        offset = int_tuple(engine_element.find('offset').attrib.values())
    offset = pygame.Vector2(offset)

    styles = []
    animations = []
    shapes = []
    for shape_elements in root.findall('shapes'):
        for shape_element in shape_elements:
            shape_class = tag2class[shape_element.tag]
            shape = shape_class.from_attrib(**shape_element.attrib)
            shapes.append(shape)
            # animate
            for animate_element in shape_element.findall('animate'):
                animate = Animate.from_attrib(animate_element.attrib.copy(), shape)
                animations.append(animate)
            # style
            for style_element in shape_element.findall('.//style'):
                attrib = style_element.attrib.copy()
                color = pygame.Color(attrib.pop('color'))
                width = int(attrib.pop('width'))
                style = Style(obj=shape, color=color, width=width)
                styles.append(style)

    # animations referencing shapes
    for animate_element in root.findall('.//animate[@href]'):
        element_attrib = animate_element.attrib.copy()
        href = element_attrib.pop('href').lstrip('#')
        for shape in shapes:
            if getattr(shape, 'id', None) == href:
                break
        else:
            raise ValueError(f'{href} not found.')
        animate = Animate.from_attrib(element_attrib, shape)
        animations.append(animate)

    for animation_element in root.findall('.//animation'):
        repeat = animation_element.attrib.get('repeat', 'none')

        objects = []
        for object_element in animation_element.findall('object'):
            href = object_element.attrib['href'].lstrip('#')
            for shape in shapes:
                if getattr(shape, 'id', None) == href:
                    break
            else:
                raise ValueError(f'{href} not found.')
            objects.append(shape)

        for obj in objects:
            for animate_element in animation_element.findall('animate'):
                attrib = animate_element.attrib.copy()
                attrib['obj'] = obj
                animate = Animate.from_attrib(**attrib)
                animations.append(animate)

    systems = SimpleNamespace(
        offset = offset,
        styles = styles,
        animations = animations,
        shapes = shapes,
    )
    return systems

def run(display_size, framerate, systems):
    default_style = Style(color='magenta', width=1)
    clock = pygame.time.Clock()
    running = True
    time = 0
    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    systems.offset += event.rel
        # draw
        screen.fill('black')
        for shape in systems.shapes:
            for style in systems.styles:
                if getattr(style, 'obj', None) == shape:
                    break
            else:
                style = default_style
            shape.draw(screen, style.color, style.width, systems.offset)
        pygame.display.flip()
        # animate
        for animate in systems.animations:
            animate.update(time)
        #
        elapsed = clock.tick(framerate)
        time += elapsed

def href_id(s):
    return s.lstrip('#')

anytag_re = re.compile(r'[a-z]+')

class AllMatch:

    def __init__(self, *regular_expressions):
        self.regular_expressions = list(map(re.compile, regular_expressions))

    def __call__(self, *values):
        items = zip(self.regular_expressions, values)
        return all(re_.match(value) for re_, value in items)


anyname = '[a-z]+'

def points_converter(string):
    return tuple(int_tuple(tuple_string.split(',')) for tuple_string in string.split())

attribute_converters = {
    AllMatch(anyname, 'id'): str,
    AllMatch(anyname, 'href'): href_id,
    AllMatch(anyname, 'color'): pygame.Color,
    AllMatch(anyname, 'points'): points_converter,
    AllMatch('animate|animation', 'repeat'): str,
    AllMatch('animate', 'attribute'): str,
    AllMatch(anyname, anyname): int,
}

def get_converter(tag, key):
    for matcher, converter in attribute_converters.items():
        if matcher(tag, key):
            return converter

def convert_attributes(tag, attrib):
    for key, val in attrib.items():
        converter = get_converter(tag, key)
        yield (key, converter(val))

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'xml',
        type = argparse.FileType(),
    )
    args = parser.parse_args(argv)

    tree = ElementTree.parse(args.xml)
    root = tree.getroot()

    for element in root.iter():
        attrs = dict(convert_attributes(element.tag, element.attrib))
        print((element, attrs))

    return
    systems = system_from_xml(args.xml)
    run(args.display_size, args.framerate, systems)

if __name__ == '__main__':
    main()
