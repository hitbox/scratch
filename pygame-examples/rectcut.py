import argparse
import contextlib
import itertools as it
import json
import math
import operator
import os
import random
import string
import unittest

from abc import ABC
from abc import abstractmethod
from collections import deque
from functools import partial
from operator import attrgetter
from types import SimpleNamespace

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

# events
STATESWITCH = pygame.event.custom_type()
DEMOCUTRECT = pygame.event.custom_type()
SWITCHMODE = pygame.event.custom_type()

# nicer ways to deal with pygame.Rect sides
SIDES = ['top', 'right', 'bottom', 'left']
SIDES_GETTERS = [attrgetter(attr) for attr in SIDES]

OPPOSITE_BY_NAME = {s: SIDES[i % len(SIDES)] for i, s in enumerate(SIDES, start=2)}

# index-aligned opposite side
OPPOSITE_SIDES = [SIDES[i % len(SIDES)] for i, s in enumerate(SIDES, start=2)]

# attributes in the correct order for combining into attribute names for pygame.Rect
SIDES_ATTR_ORDER = ['top', 'bottom', 'left', 'right']

# attribute names adjacent to key
# e.g.: 'top' -> ('left', 'right')
SIDE_ADJACENTS = {
    # side name (attribute) -> two-tuple of side attributes
    side: tuple(SIDES[(SIDES.index(side) + delta) % len(SIDES)] for delta in [-1, 1])
    for side in SIDES
}

SIDE_ADJACENTS_GETTERS = {side: attrgetter(*attrs) for side, attrs in SIDE_ADJACENTS.items()}

# SIDES_ADJACENT_CORNERS = {...} at bottom

# index-aligned positional attribute equivalent to a side
SIDEPOS = ['y', 'x'] * 2

SIDEPOS_GETTERS = [attrgetter(attr) for attr in SIDEPOS]

SIDEPOS_BY_NAME = dict(zip(SIDES, SIDEPOS))

# index-aligned side name to its appropriate dimension
SIDEDIMENSION = ['height', 'width'] * 2

SIDEDIMENSION = dict(zip(SIDES, ['height', 'width']*2))

class TestResizeSide(unittest.TestCase):

    def setUp(self):
        self.r = pygame.Rect(0, 0, 10, 10)

    def test_resize_side_top(self):
        resize_side_ip(self.r, 'top', 2)
        self.assertEqual(self.r, pygame.Rect(0, 2, 10, 8))

    def test_resize_side_left(self):
        resize_side_ip(self.r, 'left', 2)
        self.assertEqual(self.r, pygame.Rect(2, 0, 8, 10))

    def test_resize_side_right(self):
        resize_side_ip(self.r, 'right', 2)
        self.assertEqual(self.r, pygame.Rect(0, 0, 12, 10))

    def test_resize_side_bottom(self):
        resize_side_ip(self.r, 'bottom', 2)
        self.assertEqual(self.r, pygame.Rect(0, 0, 10, 12))


class TestCutRect(unittest.TestCase):

    w = h = 10

    def setUp(self):
        self.r = pygame.Rect(0, 0, self.w, self.h)

    def test_cut_rect_ip_top(self):
        remaining = cut_rect_ip(self.r, 'top', 2)
        self.assertEqual(self.r, pygame.Rect(0, 2, self.w, self.h - 2))
        self.assertEqual(remaining, pygame.Rect(0, 0, self.w, 2))

    def test_cut_rect_ip_right(self):
        remaining = cut_rect_ip(self.r, 'right', 2)
        self.assertEqual(self.r, pygame.Rect(0, 0, self.w - 2, self.h))
        self.assertEqual(remaining, pygame.Rect(self.w - 2, 0, 2, self.w))

    def test_cut_rect_ip_bottom(self):
        remaining = cut_rect_ip(self.r, 'bottom', 2)
        self.assertEqual(self.r, pygame.Rect(0, 0, self.w, self.h - 2))
        self.assertEqual(remaining, pygame.Rect(0, self.h - 2, self.w, 2))

    def test_cut_rect_ip_left(self):
        remaining = cut_rect_ip(self.r, 'left', 2)
        self.assertEqual(self.r, pygame.Rect(2, 0, self.w - 2, self.h))
        self.assertEqual(remaining, pygame.Rect(0, 0, 2, self.h))

    def test_cut_rect_ip_x(self):
        remaining = cut_rect_ip_x(self.r, 4)
        self.assertEqual(self.r, pygame.Rect(0, 0, 4, self.h))
        self.assertEqual(remaining, pygame.Rect(4, 0, 6, self.h))


class TestAdjacentSideCorners(unittest.TestCase):

    def test_adjacent_side_corners(self):
        # NOTE: attributes sorted clockwise
        self.assertEqual(get_adjacent_corners('top'), ('topleft', 'topright'))
        self.assertEqual(get_adjacent_corners('bottom'), ('bottomright', 'bottomleft'))
        self.assertEqual(get_adjacent_corners('left'), ('bottomleft', 'topleft'))
        self.assertEqual(get_adjacent_corners('right'), ('topright', 'bottomright'))


class TestSharesSide(unittest.TestCase):

    def test_shares_side(self):
        # exactly shares
        self.assertEqual(
            shares_side(
                pygame.Rect(0,0,10,10),
                pygame.Rect(10,0,10,10),
                0,
            ),
            ('right', 'left'),
        )
        # order is important
        self.assertEqual(
            shares_side(
                pygame.Rect(10,0,10,10),
                pygame.Rect(0,0,10,10),
                0,
            ),
            ('left', 'right'),
        )

    def test_does_not_share_sides(self):
        # adjacents are off (vertical)
        self.assertNotEqual(
            shares_side(
                pygame.Rect(0,0,10,10),
                pygame.Rect(10,10,10,10),
                0,
            ),
            ('right', 'left'),
        )


class EventHandler:

    userevent_names = {}

    def __getitem__(self, event_type):
        if event_type >= pygame.USEREVENT:
            event_name = self.userevent_names[event_type]
        else:
            event_name = pygame.event.event_name(event_type).lower()
        method_name = f'on_{event_name}'
        return getattr(self, method_name)


class BaseState(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def events(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass


class EventDispatchMixin:
    "Dispath to event handler by method name mixin."

    def events(self):
        for event in pygame.event.get():
            name = callable_name_for_event(event)
            method = getattr(self, name, None)
            if method:
                method(event)


class RectStateBase(EventDispatchMixin, BaseState):

    def on_quit(self, event):
        # stop state engine
        post_stateswitch(None)


class RectCutState(RectStateBase):
    "Rect cutting state/tool"

    def __init__(self):
        # XXX: dupes be here with TilingManagerState
        self.font = pygame.font.SysFont('arial', 32)
        self.screen = pygame.display.get_surface()
        self.frame = self.screen.get_rect()
        self.rect_renderer = RectRenderer(global_palettes['beach'])
        #
        self.preview_cut_line = None
        self.cut_sides = it.cycle(SIDES)
        self.next_cut_side()
        self.started = 0

    def start(self):
        cursor = pygame.SYSTEM_CURSOR_ARROW
        pygame.mouse.set_cursor(cursor)
        if self.started == 0:
            initial_rect = inflate_by(self.frame, -.20)
            global_rects.append(initial_rect)
        self.started += 1
        self.update_preview_cut_line(pygame.mouse.get_pos(), global_rects)

    def on_keydown(self, event):
        if event.key in (pygame.K_TAB, pygame.K_q):
            post_stateswitch(TilingManagerState)
        elif event.key == pygame.K_LALT:
            self.next_cut_side()
        elif event.key == pygame.K_ESCAPE:
            post_stateswitch(None)

    def on_mousemotion(self, event):
        self.update_preview_cut_line(event.pos, global_rects)

    def on_mousebuttondown(self, event):
        if event.button != pygame.BUTTON_LEFT:
            return
        rect = get_colliding_rect(event.pos, global_rects)
        if not rect:
            return
        remaining = cut_at_position(rect, event.pos, self.cut_side)
        global_rects.append(remaining)

    def next_cut_side(self):
        self.cut_side = next(self.cut_sides)
        self.update_preview_cut_line(pygame.mouse.get_pos(), global_rects)

    def update_preview_cut_line(self, pos, rects):
        rect = get_colliding_rect(pos, rects)
        if not rect:
            self.preview_cut_line = None
        else:
            self.preview_cut_line = make_preview_cut_line(rect, pos, self.cut_side)

    def update(self):
        pass

    def draw(self):
        self.screen.fill('black')
        # draw rects
        self.rect_renderer.render(self.screen, global_rects)
        # preview cut line
        if self.preview_cut_line:
            p1, p2 = self.preview_cut_line
            pygame.draw.line(self.screen, 'red', p1, p2, 1)
        # this state's name
        image = self.font.render(self.__class__.__name__, True, 'white')
        rect = image.get_rect(bottomright=self.frame.bottomright)
        self.screen.blit(image, rect)
        pygame.display.flip()


class TilingManagerState(RectStateBase):
    "Tiling window manager state"

    def __init__(self):
        # XXX: dupes be here with RectCutState
        self.font = pygame.font.SysFont('arial', 32)
        self.screen = pygame.display.get_surface()
        self.frame = self.screen.get_rect()
        self.rect_renderer = RectRenderer(global_palettes['beach'])
        #
        self.dragging = None

    def start(self):
        pass

    def on_keydown(self, event):
        if event.key in (pygame.K_TAB, pygame.K_q):
            post_stateswitch(RectJoinState)
        elif event.key == pygame.K_ESCAPE:
            post_stateswitch(None)

    def on_mousebuttondown(self, event):
        self.dragging = make_dragging(global_rects, event.pos)

    def on_mousebuttonup(self, event):
        self.dragging = None

    def on_mousemotion(self, event):
        self.update_mousecursor(event.pos)
        if not self.dragging:
            return
        unpack_tiling_drag(self.dragging, event.rel)

    def update_mousecursor(self, pos):
        dragging = make_dragging(global_rects, pos)
        cursor = cursor_from_dragging(dragging)
        pygame.mouse.set_cursor(cursor)

    def update(self):
        pass

    def draw(self):
        self.screen.fill('black')
        self.rect_renderer.render(self.screen, global_rects)
        # this state's name
        image = self.font.render(self.__class__.__name__, True, 'white')
        rect = image.get_rect(bottomright=self.frame.bottomright)
        self.screen.blit(image, rect)
        pygame.display.flip()


class RectJoinState(RectStateBase):
    "Join rects with others that exactly share a side"

    def __init__(self):
        # XXX: dupes be here with RectCutState
        self.font = pygame.font.SysFont('arial', 32)
        self.screen = pygame.display.get_surface()
        self.frame = self.screen.get_rect()
        self.rect_renderer = RectRenderer(global_palettes['beach'])

    def start(self):
        self.clicked_rect = None
        self.closest_rect_by_side = None

    def on_keydown(self, event):
        if event.key in (pygame.K_TAB, pygame.K_q):
            post_stateswitch(RectCutState)
        elif event.key == pygame.K_ESCAPE:
            post_stateswitch(None)

    def on_mousebuttondown(self, event):
        if event.button != pygame.BUTTON_LEFT:
            return
        for rect in global_rects:
            if rect.collidepoint(event.pos):
                self.clicked_rect = rect
                break
        else:
            self.clear_join()

    def on_mousebuttonup(self, event):
        if (
            event.button == pygame.BUTTON_LEFT
            and self.clicked_rect
            and self.closest_rect_by_side
        ):
            new_rect = wrap(self.clicked_rect, self.closest_rect_by_side)
            global_rects.remove(self.clicked_rect)
            global_rects.remove(self.closest_rect_by_side)
            global_rects.append(new_rect)
        self.clear_join()

    def clear_join(self):
        self.clicked_rect = None
        self.closest_rect_by_side = None

    def on_mousemotion(self, event):
        if not self.clicked_rect:
            return

        self.closest_rect_by_side = closest_join_rect(
            self.clicked_rect, event.pos, global_rects
        )

        if self.closest_rect_by_side:
            cursor = cursor_for_rect_diff(self.clicked_rect, self.closest_rect_by_side)
            pygame.mouse.set_cursor(cursor)

    def update(self):
        pass

    def draw(self):
        self.screen.fill('black')
        self.rect_renderer.render(self.screen, global_rects)
        # this state's name
        image = self.font.render(self.__class__.__name__, True, 'white')
        rect = image.get_rect(bottomright=self.frame.bottomright)
        self.screen.blit(image, rect)
        #
        if self.clicked_rect and self.closest_rect_by_side:
            pygame.draw.rect(self.screen, 'magenta', self.closest_rect_by_side, 8)
        pygame.display.flip()


class RectRenderer:
    "Render pygame rects"

    def __init__(self, colors, width=4):
        self.colors = colors
        self.width = width

    def render(self, surf, rects, highlight=None):
        # TODO
        # - would like a way to pass in rects to be styled specifically but
        #   rects aren't hashable.
        for index, rect in enumerate(rects):
            color = self.colors[index % len(self.colors)]
            width = self.width
            if highlight and rect in highlight:
                color = 'red'
                width = 4
            pygame.draw.rect(surf, color, rect, width)


get_top, get_right, get_bottom, get_left = map(attrgetter, SIDES)

get_sides = attrgetter(*SIDES)

def callable_name_for_event(event):
    event_name = pygame.event.event_name(event.type)
    callable_name = f'on_{event_name.lower()}'
    return callable_name

def palettes_from_json(path):
    with open(path) as json_file:
        json_data = json.load(json_file)
        return json_data

def first_or_none(iterable):
    try:
        return next(iterable)
    except StopIteration:
        pass

def closest_join_rect(rect, pos, rects):
    # all rects the one that is clicked on can join to
    joinable = [
        other for other in rects
        if other is not rect and shares_side(rect, other)
    ]

    # if the cursor is in exactly one of the joinable rects, indicate that one.
    colliding_joinable = [other for other in joinable if other.collidepoint(pos)]
    if len(colliding_joinable) == 1:
        return colliding_joinable[0]
    else:
        # otherwise, choose the rect with the side closest to the cursor
        def closest_side(rect):
            closest_line_to_cursor = min(
                distance_to_line(pos, side_line_getter(rect))
                for side_line_getter in SIDES_ADJACENT_CORNERS_GETTERS.values()
            )
            return closest_line_to_cursor

        closest_rect_by_side = min(joinable, key=closest_side)
        return closest_rect_by_side

def cursor_for_rect_diff(r1, r2):
    dx = r1.x - r2.x
    dy = r1.y - r2.y
    assert dx == 0 or dy == 0
    # there's no built cursors for point in one direction, just double
    # pointers for WE and NS.
    if dx:
        cursor = pygame.SYSTEM_CURSOR_SIZEWE
    else:
        cursor = pygame.SYSTEM_CURSOR_SIZENS
    return cursor

def wrap(*rects):
    """
    Return bounding rect for rects.
    """
    sides = zip(*map(get_sides, rects))
    tops, rights, bottoms, lefts = sides
    top = min(tops)
    right = max(rights)
    bottom = max(bottoms)
    left = min(lefts)
    width = right - left
    height = bottom - top
    return pygame.Rect(left, top, width, height)

def overlap(r1, r2):
    # assumes colliding
    _, left, right, _ = sorted([r1.left, r1.right, r2.left, r2.right])
    _, top, bottom, _ = sorted([r1.top, r1.bottom, r2.top, r2.bottom])
    width = right - left
    height = bottom - top
    return pygame.Rect(left, top, width, height)

def get_adjacent_corners(side):
    adjacent1, adjacent2 = SIDE_ADJACENTS[side]
    corner_attr1 = ''.join(sorted([side, adjacent1], key=SIDES_ATTR_ORDER.index))
    corner_attr2 = ''.join(sorted([side, adjacent2], key=SIDES_ATTR_ORDER.index))
    return (corner_attr1, corner_attr2)

def get_side_line(rect, side):
    # attribute names for either side of `side` name
    corner_attr1, corner_attr2 = SIDES_ADJACENT_CORNERS[side]
    return (getattr(rect, corner_attr1), getattr(rect, corner_attr2))

def sorted_groupby(iterable, key=None):
    return it.groupby(sorted(iterable, key=key), key=key)

def grouped_sides(rects):
    """
    Group rects by their sides and the value of that side
    e.g.: ('right', 42) -> [list of rects where rect.right == 42]
    """
    grouped_by_sides_and_values = {
        (side_name, side_value): list(sharing_rects)
        for side_name, side_getter in zip(SIDES, SIDES_GETTERS)
        for side_value, sharing_rects in sorted_groupby(rects, key=side_getter)
    }
    return grouped_by_sides_and_values

def grouped_side_lines(rects):
    grouped = {
        (side_name, line_value): list(sharing_rects)
        for side_name, line_getter in SIDES_ADJACENT_CORNERS_GETTERS.items()
        for line_value, sharing_rects in sorted_groupby(rects, key=line_getter)
    }
    return grouped

def get_line_parts(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    a = y1 - y2
    b = x1 - x2
    c = x1 * y2 - x2 * y1
    return (a, b, c)

def distance_to_line(point, line):
    p1, p2 = line
    x1, y1 = p1
    x2, y2 = p2
    a, b, c = get_line_parts(p1, p2)
    return abs(a * x1 + b * y1 + c) / math.sqrt(a * a + b * b)

def make_preview_cut_line(rect, pos, cut_side):
    # assumes pos(ition) colliding rect
    x, y = pos
    if cut_side in ('top', 'bottom'):
        line = ((rect.left, y), (rect.right, y))
    else:
        line = ((x, rect.top), (x, rect.bottom))
    return line

def make_dragging(rects, pos):
    """
    Try to make a four-tuple of sides and groups that are connected by opposite sides.
    """
    # assumes rects arranged like cut_rect_ip results.
    for rect in global_rects:
        if rect.collidepoint(pos):
            break
    else:
        return

    # side_value_grouped: grouped by side and value of side,
    # e.g.: ('top', 10) -> [rects...]
    #       a list of rects, all of whose top attr is 10
    side_value_grouped = grouped_sides(global_rects)
    closest_side_name = closest_side(rect, pos)
    closest_side_value = getattr(rect, closest_side_name)

    # Is there is another group of rects with the same side value but for
    # the opposite side name?
    opposite_side_name = OPPOSITE_BY_NAME[closest_side_name]
    opposite_key = (opposite_side_name, closest_side_value)
    oppo_group = side_value_grouped.get(opposite_key)
    if not oppo_group:
        return

    side_group = side_value_grouped[(closest_side_name, closest_side_value)]
    dragging = (closest_side_name, side_group, opposite_side_name, oppo_group)
    return dragging

def cursor_from_dragging(dragging):
    if not dragging:
        cursor = pygame.SYSTEM_CURSOR_ARROW
    else:
        side, *ignore = dragging
        if side in ('top', 'bottom'):
            cursor = pygame.SYSTEM_CURSOR_SIZENS
        else:
            cursor = pygame.SYSTEM_CURSOR_SIZEWE
    return cursor

def tiling_drag(side1, group1, side2, group2, amount):
    args = [(group1, side1), (group2, side2)]
    for rectgroup, side in args:
        for rect in rectgroup:
            resize_side_ip(rect, side, amount)

def unpack_tiling_drag(dragging, relpos):
    side1, group1, side2, group2 = dragging
    reldict = dict(zip('xy', relpos))
    amount = reldict[SIDEPOS_BY_NAME[side1]]
    tiling_drag(side1, group1, side2, group2, amount)

def closest_side(rect, point):
    # for attribute access to x and y
    point = pygame.Vector2(point)
    side_distance = {
        side_name: abs(side_getter(rect) - pos_getter(point))
        for side_name, side_getter, pos_getter
        in zip(SIDES, SIDES_GETTERS, SIDEPOS_GETTERS)
    }
    closest_side = min(side_distance, key=side_distance.get)
    return closest_side

def shares_side(r1, r2, threshold=0):
    """
    Condition two rects share a side within a threshold. The rects must share
    adjacent sides exactly.
    """
    for side, oppo in zip(SIDES, OPPOSITE_SIDES):
        r1side = getattr(r1, side)
        r2side = getattr(r2, oppo)
        # adjacents of either side or oppo should be same
        get_adjacents = SIDE_ADJACENTS_GETTERS[side]
        if (
            abs(r1side - r2side) <= threshold
            and get_adjacents(r1) == get_adjacents(r2)
        ):
            return (side, oppo)

def get_rect(*args, **kwargs):
    """
    :param *args:
        Optional rect used as base. Otherwise new (0,)*4 rect is created.
    :param kwargs:
        Keyword arguments to set on new rect.
    """
    if len(args) not in (0, 1):
        raise ValueError()
    if len(args) == 1:
        result = args[0].copy()
    else:
        result = pygame.Rect((0,)*4)
    for key, val in kwargs.items():
        setattr(result, key, val)
    return result

def resize_side_ip(rect, side, amount):
    """
    Resize a rect's side, in place, accounting for the sides top and left
    moving the rect.
    """
    dimension = SIDEDIMENSION[side]
    dimension_amount = getattr(rect, dimension)
    if side in ('top', 'left'):
        setattr(rect, side, (getattr(rect, side) + amount))
        dimension_amount -= amount
    else:
        dimension_amount += amount
    setattr(rect, dimension, dimension_amount)

def cut_rect_ip_x(rect, xpos):
    "Cut rect in place on horizontal position. Rects will share a side."
    # TODO: is this a good function?
    left, middle, right = sorted([rect.left, xpos, rect.right])
    rect.width = middle - left
    remaining = pygame.Rect(middle, rect.top, right - middle, rect.height)
    return remaining

def cut_rect_ip(rect, side, amount):
    """
    Cut a rect side by amount, in place; and return a new rect that fits inside
    the cut out part.
    """
    result = rect.copy()
    # size new rect
    dimension = SIDEDIMENSION[side]
    setattr(result, dimension, amount)
    # align new rect to same side being cut
    setattr(result, side, getattr(rect, side))
    # in place resize rect for cut
    resize_amount = amount
    if side in ('right', 'bottom'):
        resize_amount = -resize_amount
    resize_side_ip(rect, side, resize_amount)
    return result

def cut_at_position(rect, pos, side):
    posdict = dict(zip('xy', pos))
    poskey = SIDEPOS_BY_NAME[side]
    amount = abs(getattr(rect, side) - posdict[poskey])
    remaining = cut_rect_ip(rect, side, amount)
    return remaining

def post_stateswitch(state_class, **data):
    event = pygame.event.Event(STATESWITCH, state_class=state_class, **data)
    pygame.event.post(event)

def inflate_by(rect, fraction):
    return rect.inflate(rect.width*fraction, rect.height*fraction)

def get_colliding_rect(position, rects):
    for rect in rects:
        if rect.collidepoint(position):
            return rect

def run(
    state_class,
    output_string = None,
):
    "Run state engine"
    next_state = None
    state = state_class()
    state_instances = set([state])
    running = True
    state.start()
    while running:
        # events only the engine should see
        for event in pygame.event.get():
            if event.type != STATESWITCH:
                pygame.event.post(event)
            else:
                # STATESWITCH event
                if event.state_class is None:
                    running = False
                else:
                    # try to get already created instance
                    next_state = first_or_none(
                        instantiated
                        for instantiated in state_instances
                        if event.state_class
                        and isinstance(instantiated, event.state_class)
                    )
                    if next_state is None:
                        next_state = event.state_class()
                        state_instances.add(next_state)
        if next_state:
            # change state
            state = next_state
            state.start()
            next_state = None
        else:
            state.events()
            state.update()
            state.draw()

def start(options):
    """
    Initialize and start run loop. Bridge between options and main loop.
    """
    pygame.font.init()
    pygame.display.set_mode(options.size)
    #run(output_string=options.output, demo_mode=options.demo)
    run(RectCutState)

def sizetype(string):
    """
    Parse string into a tuple of integers.
    """
    size = tuple(map(int, string.replace(',', ' ').split()))
    if len(size) == 1:
        size += size
    return size

def cli():
    # https://halt.software/dead-simple-layouts/
    # TODO
    # [X] generic function taking sidename to cut
    # [ ] non-inplace versions? does that make sense? what's the use?
    # [X] resize bordering rects like tiling window manager
    # [ ] limit resizing in tiling mode
    # [ ] try to keep ratio of rects affected?
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--size',
        default = '800,800',
        type = sizetype,
        help = 'Screen size. Default: %(default)s',
    )
    parser.add_argument(
        '--demo',
        action = 'store_true',
        help = 'Automatic demo cutting rects.',
    )
    parser.add_argument(
        '--output',
        help = 'Format string for frame output.',
    )
    args = parser.parse_args()
    start(args)

# needed to wait for get_adjacent_corners function
# sides to two-tuple attribute names, forming line for that side
# e.g.: 'top' -> ('topleft', 'topright')
SIDES_ADJACENT_CORNERS = {side: get_adjacent_corners(side) for side in SIDES}

# side key -> a getter for that side's line
# e.g.: 'top' -> attrgetter('topleft', 'topright')
SIDES_ADJACENT_CORNERS_GETTERS = {
    side: attrgetter(*attrs) for side, attrs in SIDES_ADJACENT_CORNERS.items()
}

if __name__ == '__main__':
    # unsure how to share between states, especially when the engine controls when
    # they're instantiated.
    global_palettes = palettes_from_json('palettes.json')['palettes']

    global_rects = []

    cli()
