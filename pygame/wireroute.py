import fileinput
import itertools as it
import operator as op
import os
import pickle

import pygamelib

from pygamelib import pygame
from trirectcoll import triangle_rect_collision

class WireDemo(pygamelib.DemoBase):

    def __init__(self, rects, wire, colors, font):
        self.rects = rects
        self.wire = wire
        self.colors = colors
        self.font = font

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()
        elif event.key == pygame.K_SPACE:
            self.wire.reset()
            self.wire.update(pygame.mouse.get_pos(), self.rects)
            pygamelib.post_videoexpose()

    def do_mousemotion(self, event):
        self.wire.update(event.pos, self.rects)
        pygamelib.post_videoexpose()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        for rect in self.rects:
            pygame.draw.rect(self.screen, 'azure', rect, 1)
        for line in it.pairwise(self.wire.points):
            start, end = line
            pygame.draw.line(self.screen, 'magenta', start, end, 1)

        last = self.wire.points[-1]
        mpos = pygame.mouse.get_pos()
        pygame.draw.line(self.screen, 'magenta', last, mpos, 1)

        lines = [
            f'{len(self.wire.points)}',
            f'{self.wire.points}',
        ]
        images = [self.font.render(line, True, 'azure') for line in lines]
        rects = [image.get_rect() for image in images]
        pygamelib.flow_topbottom(rects)
        pygamelib.move_as_one(rects, bottomleft=self.window.bottomleft)
        for image, rect in zip(images, rects):
            self.screen.blit(image, rect)

        pygame.display.flip()


class Wire:

    def __init__(self, initial_point):
        self.initial_point = initial_point
        self.reset()

    def reset(self):
        self.points = [self.initial_point]

    def update(self, end, rects):
        iitem = intersection_item_nearest_start(self.points[-1], end, rects)
        if iitem:
            point, rect = iitem

            corners = list(pygamelib.corners(rect))
            if not any(corner == point for corner in corners):
                point = nearest_corner(self.points[-1], end, point, rect)

            for name, corner in zip(pygamelib.CORNERNAMES, corners):
                if point == corner:
                    newpoint = inflate_point_by_side(point, name)
                    self.points.append(newpoint)
                    break
        elif len(self.points) > 1:
            triangle = self.points[-2:] + [end]
            if not any(
                triangle_rect_collision(triangle, list(pygamelib.corners(rect)))
                for rect in rects
            ):
                self.points.pop()


def color_predicate(color):
    return len(set(color[:3])) > 1

def color_order(color):
    return color.hue and color.saturation

def get_colors():
    colors = map(
        pygamelib.ColorAttributes,
        pygamelib.UNIQUE_THECOLORS.values()
    )
    colors = filter(color_predicate, colors)
    return sorted(colors, key=color_order)

def intersection_items(line, rects):
    for rect in rects:
        for intersection in pygamelib.line_rect_intersections(line, rect):
            yield (intersection, rect)

def intersection_item_nearest_start(start, end, rects):
    def key(item):
        point, rect = item
        return pygame.Vector2(point).distance_to(start)

    rects = map(pygame.Rect, rects)
    items = intersection_items((start, end), rects)
    items = sorted(items, key=key)
    if items:
        return items[0]

def nearest_corner(start, end, intersect, rect):
    def predicate(corner):
        line = (corner, end)
        intersections = pygamelib.line_rect_intersections(line, rect)
        return len(set(intersections)) < 2

    def distance(point):
        return (
            pygame.Vector2(point).distance_to(intersect)
            + pygame.Vector2(intersect).distance_to(end)
        )

    corners = filter(predicate, pygamelib.corners(rect))
    corners = sorted(corners, key=distance)
    if corners:
        return corners[0]

def inflate_point_by_side(point, name, delta=1):
    x, y = point
    if name == 'topleft':
        return (x - delta, y - delta)
    elif name == 'topright':
        return (x + delta, y - delta)
    elif name == 'bottomright':
        return (x + delta, y + delta)
    elif name == 'bottomleft':
        return (x - delta, y + delta)

def run(display_size, rects):
    frame = pygame.Rect((0,)*2, display_size)
    frame.inflate_ip((-min(display_size)*0.5,)*2)
    thickness = min(frame.size) / 8

    line_start = (500,600)
    colors = [color for index, color in enumerate(get_colors()) if index % 8 == 0]
    font = pygamelib.monospace_font(15)
    wire = Wire(line_start)
    state = WireDemo(rects, wire, colors, font)
    pygame.display.set_mode(display_size)
    engine = pygamelib.Engine()
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'rects',
    )
    args = parser.parse_args(argv)

    if args.rects == '-':
        rects = list(map(pygamelib.rect_type, fileinput.input()))
    elif os.path.exists(rectspath):
        with open(rectspath, 'rb') as rectsfile:
            rects = pickle.load(rectsfile)
    else:
        rects = [frame.inflate((-min(frame.size)*.70,)*2)]

    frame = pygame.Rect((0,)*2, args.display_size)
    pygamelib.move_as_one(rects, center=frame.center)
    run(args.display_size, rects)

if __name__ == '__main__':
    main()

# 2024-02-01
# - dated late
# - wanted to make a system where you can wrap a "wire" around rects.
# /home/hitbox/repos/reference/iacore/wire-routing-game
# https://www.jeffreythompson.org/collision-detection/line-line.php
# https://git.envs.net/iacore/wire-routing-game
# https://www.1a-insec.net/blog/31-wire-routing-input-scheme/
