import argparse
import functools
import itertools as it
import re

from collections import ChainMap
from collections import defaultdict
from pprint import pprint
from types import SimpleNamespace
from xml.etree import ElementTree

import pygamelib

from pygamelib import Timer
from pygamelib import matchall
from pygamelib import pygame

repeat_func = {
    'once': iter,
    'cycle': it.cycle,
}

class Animation(SimpleNamespace):
    """
    Collection of animate objects.
    """

    @classmethod
    def from_element(cls, element):
        repeat = element.attrib.get('repeat', 'once')
        container = repeat_func[repeat]
        animates = container(parse_animation(element))
        attrs = dict(convert_attributes(element))
        return cls(animates=animates, **attrs)

    def update(self, time, elapsed):
        for animate in self.animates:
            animate.update(time, elapsed)
            break

    def apply(self, data):
        for animate in self.animates:
            animate.apply(data)
            break


class Animate(SimpleNamespace):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._elapsed = 0
        self._value = None

    @classmethod
    def from_element(cls, element):
        # from and to are the type of the attribute in the object they
        # reference
        converter = get_converter(element.tag, element.attrib['attribute'])
        referenced = {}
        if 'from' in element.attrib:
            referenced['from_'] = converter(element.attrib.pop('from'))
        if 'to' in element.attrib:
            referenced['to'] = converter(element.attrib.pop('to'))

        start = int(element.attrib.pop('start'))
        duration = int(element.attrib.pop('dur'))
        # TODO
        # - maybe another <tag> to say "this is a list of animates, run them
        #   one after another."
        if 'repeat' in element.attrib:
            repeat = pygamelib.repeat_type(element.attrib.pop('repeat'))
        else:
            repeat = None
        timer = Timer(start, duration, repeat)

        remaining = dict(convert_attributes(element))
        return cls(tag=element.tag, timer=timer, **referenced, **remaining)

    def update(self, time, elapsed):
        self.timer.update(elapsed)
        if not hasattr(self, 'from_'):
            self.from_ = obj[self.attribute]
        self._value = pygamelib.mix(self.timer.normtime(), self.from_, self.to)

    def apply(self, data):
        if self.timer.is_running():
            data[self.attribute] = self._value


class Shape:
    """
    A collection of primitive drawings.
    """

    def __init__(self, primitives):
        self.primitives = primitives

    def __repr__(self):
        return str(self.primitives)

    @classmethod
    def from_element(cls, element):
        primitives = list(parse_primitives(element))
        return cls(primitives)

    def draw(self, surf, offset):
        for data in self.primitives:
            renderer = tag2renderer[data['tag']]
            renderer(surf, data, offset)


class Selector:

    def __init__(self, tag_selector, class_selector):
        self.tag_selector = tag_selector
        self.class_selector = class_selector

    @classmethod
    def from_string(self, string):
        if string is None:
            string = ''
        tag_selector, _, class_selector = string.partition('.')
        return Selector(tag_selector or None, class_selector or None)

    def __call__(self, data):
        if self.tag_selector is None:
            tag_match = True
        else:
            tag_match = data['tag'] == self.tag_selector
        if self.class_selector is None:
            class_match = True
        else:
            class_match = self.class_selector in data.get('class', set())
        return tag_match and class_match


def render_circle(surf, data, offset):
    center = offset + (data['cx'], data['cy'])
    r = data['r']
    color = data['color']
    width = data['width']
    return pygame.draw.circle(surf, color, center, r, width)

def render_rect(surf, data, offset):
    topleft = offset + (data['x'], data['y'])
    size = (data['w'], data['h'])
    color = data['color']
    width = data['width']
    return pygame.draw.rect(surf, color, (topleft, size), width)

def render_lines(surf, data, offset):
    points = [offset + point for point in data['points']]
    closed = data['closed']
    color = data['color']
    width = data['width']
    return pygame.draw.lines(surf, color, closed, points, width)

def render_polygon(surf, data, offset):
    points = [offset + point for point in data['points']]
    color = data['color']
    width = data['width']
    return pygame.draw.polygon(surf, color, points, width)

def render_arc(surf, data, offset):
    x, y, w, h = data['rect']
    topleft = offset + (x, y)
    start_angle = data['start_angle']
    end_angle = data['end_angle']
    color = data['color']
    width = data['width']
    rect = (topleft, (w, h))
    return pygame.draw.arc(surf, color, rect, start_angle, end_angle, width)

def parse_primitives(element):
    for child in element:
        class_ = tag2class[child.tag]
        kwargs = dict(convert_attributes(child))
        kwargs.setdefault('tag', child.tag)
        yield class_.from_attrib(**kwargs)

def parse_primitives(element):
    for child in element:
        element_data = dict(convert_attributes(child))
        data = primitive_data[child.tag].new_child(element_data)
        yield data

def parse_animation(element):
    for child in element:
        if child.tag != 'animate':
            raise ValueError
        yield Animate.from_element(child)

def fixkey(name):
    if name == 'from':
        name = 'from_'
    return name

def system_from_xml(xml):
    tree = ElementTree.parse(xml)
    root = tree.getroot()

    engine_element = root.find('engine')
    if engine_element:
        offset = int_tuple(engine_element.find('offset').attrib.values())
    offset = pygame.Vector2(offset)

    shapes = list(map(Shape.from_element, root.iter('shape')))
    styles = list(map(dict, map(convert_attributes, root.iter('style'))))
    animations = list(map(Animation.from_element, root.iter('animation')))

    systems = SimpleNamespace(
        offset = offset,
        styles = styles,
        animations = animations,
        shapes = shapes,
    )
    return systems

def run(display_size, framerate, systems):
    clock = pygame.time.Clock()
    running = True
    time = 0
    elapsed = 0
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
            for data in shape.primitives:
                for style in systems.styles:
                    if style['select'](data):
                        data.update({k: v for k, v in style.items() if k != 'select'})
        for shape in systems.shapes:
            shape.draw(screen, systems.offset)
        pygame.display.flip()
        # animate
        for animation in systems.animations:
            animation.update(time, elapsed)

        for shape in systems.shapes:
            for data in shape.primitives:
                for style in systems.styles:
                    animation_id = style.get('animation')
                    if not animation_id:
                        continue
                    if not style['select'](data):
                        continue
                    for animation in systems.animations:
                        if animation.id == animation_id:
                            animation.apply(data)

        elapsed = clock.tick(framerate)
        time += elapsed

def href_id(s):
    return s.lstrip('#')

def points_converter(string):
    return tuple(
        int_tuple(tuple_string.split(','))
        for tuple_string in string.split()
    )

def get_converter(tag, key):
    """
    Get first converter to match or none.
    """
    for matcher, converter in attribute_converters:
        if matcher(tag, key):
            return converter

def convert_attributes(element):
    """
    Convert attributes to types and fix key for attribute name.
    """
    for key, val in element.attrib.items():
        key = fixkey(key)
        converter = get_converter(element.tag, key)
        if converter:
            yield (key, converter(val))

int_tuple = pygamelib.typed_container(tuple, int)

tags = [
    'animate',
    'animation',
    'circle',
    'engine',
    'lines',
    'polygon',
    'rect',
    'style',
    'arc',
]

anyname = '[a-z]+'

# TODO
# - cleanup
# - there are other type conversions above
attribute_converters = [
    (matchall(anyname, 'id'), str),
    (matchall(anyname, 'class'), str.split),
    (matchall(anyname, 'href'), href_id),
    (matchall('style', 'select'), Selector.from_string),
    (matchall('style', 'animation'), href_id),
    (matchall(anyname, 'color'), pygame.Color),
    (matchall(anyname, 'points'), points_converter),
    (matchall('animate|animation', 'repeat|attribute|playback'), str),
    (matchall('arc', 'start_angle|end_angle'), float),
    (matchall('arc', 'rect'), pygamelib.rect_type),
    # remaining recognized tags' attributes to int
    (matchall('|'.join(tags), anyname), int),
]

tag2renderer = {
    'circle': render_circle,
    'rect': render_rect,
    'lines': render_lines,
    'arc': render_arc,
}

default_style = dict(color='magenta', width=1)

circle_data = ChainMap(dict(
    cx = 0,
    cy = 0,
    r = 0,
    draw_top_right = None,
    draw_top_left = None,
    draw_bottom_left = None,
    draw_bottom_right = None,
    tag = 'circle',
    **default_style,
))

rect_data = ChainMap(dict(
    x = 0,
    y = 0,
    w = 0,
    h = 0,
    border_radius = 0,
    border_top_left_radius = -1,
    border_top_right_radius = -1,
    border_bottom_left_radius = -1,
    border_bottom_right_radius = -1,
    tag = 'rect',
    **default_style,
))

lines_data = ChainMap(dict(
    points = None,
    closed = False,
    tag = 'lines',
    **default_style,
))

arc_data = ChainMap(dict(
    rect = (0, 0, 0, 0),
    start_angle = 0,
    end_angle = 0,
    tag = 'arc',
    **default_style,
))

primitive_data = {
    'circle': circle_data,
    'rect': rect_data,
    'lines': lines_data,
    'arc': arc_data
}

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'xml',
        type = argparse.FileType(),
    )
    parser.add_argument(
        '--dump',
        action = 'store_true',
    )
    args = parser.parse_args(argv)
    systems = system_from_xml(args.xml)
    if args.dump:
        pprint(systems)
        return
    run(args.display_size, args.framerate, systems)

if __name__ == '__main__':
    main()
