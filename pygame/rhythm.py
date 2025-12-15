import argparse
import math
import contextlib
import os
import random

from operator import attrgetter

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

from pygame import Rect

getbounds = attrgetter('left', 'top', 'right', 'bottom')

def up_arrow(rect):
    left_elbow = rect.left + rect.width / 4
    right_elbow = rect.left + rect.width * 0.75
    yield rect.midtop
    yield rect.midright
    yield (right_elbow, rect.centery)
    yield (right_elbow, rect.centery)
    yield (right_elbow, rect.bottom)
    yield (left_elbow, rect.bottom)
    yield (left_elbow, rect.centery)
    yield rect.midleft

def left_arrow(rect):
    top_elbow = rect.top + rect.height / 4
    bottom_elbow = rect.top + rect.height * 0.75
    yield rect.midleft
    yield rect.midtop
    yield (rect.centerx, top_elbow)
    yield (rect.right, top_elbow)
    yield (rect.right, bottom_elbow)
    yield (rect.centerx, bottom_elbow)
    yield rect.midbottom

def right_arrow(rect):
    top_elbow = rect.top + rect.height / 4
    bottom_elbow = rect.top + rect.height * 0.75
    yield rect.midright
    yield rect.midtop
    yield (rect.centerx, top_elbow)
    yield (rect.left, top_elbow)
    yield (rect.left, bottom_elbow)
    yield (rect.centerx, bottom_elbow)
    yield rect.midbottom

points_funcs = {
    pygame.K_UP: up_arrow,
    pygame.K_LEFT: left_arrow,
    pygame.K_RIGHT: right_arrow,
}

class AlignmentKey:

    def __init__(self, anchor_attr, attribute, spacing=None):
        self.anchor_attr = anchor_attr
        self.attribute = attribute
        self.spacing = spacing

    def __call__(self, rect1, rect2):
        spacing = self.spacing
        if spacing is None:
            spacing = 0
        setattr(rect2, self.attribute, getattr(rect1, self.anchor_attr) + spacing)


class Note(pygame.sprite.Sprite):

    def __init__(self, key, rect, groups=None):
        self.key = key
        self.rect = rect
        self.velocity = pygame.Vector2()
        if groups is None:
            groups = tuple()
        super().__init__(*groups)

    def draw(self, surface, color):
        pfunc = points_funcs[self.key]
        pygame.draw.polygon(surface, color, list(pfunc(self.rect)), 1)


class Lane:

    def __init__(self, target, notes, index=None):
        self.target = target
        self.notes = notes
        if index is None:
            index = -1
        self.index = index

    @property
    def current(self):
        def distance_to_target(note):
            return math.dist(note.rect.center, self.target.center)

        closest = min(self.notes, key=distance_to_target)
        return closest

    @property
    def rects(self):
        return [note.rect for note in self.notes]


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--pattern',
        choices=list(pattern_functions),
        default = 'sine',
    )
    parser.add_argument(
        '--frequency',
        type = float,
        default = 2.0,
    )
    return parser

def sine_wave_spacing(i, n, min_space=40, max_space=120, frequency=1.0):
    """
    Generate spacing using sine wave for smooth rhythmic patterns
    """
    # Normalize i to 0-1 range
    t = i / n
    # Apply sine wave
    wave = math.sin(2 * math.pi * frequency * t)
    # Map from [-1, 1] to [min_space, max_space]
    spacing = min_space + (max_space - min_space) * (wave + 1) / 2
    return int(spacing)

pattern_functions = {
    'sine': sine_wave_spacing,
}

def align(rects, key):
    for r1, r2 in zip(rects, rects[1:]):
        key(r1, r2)

def align_with_pattern(rects, func):
    n = len(rects)
    for i, (r1, r2) in enumerate(zip(rects, rects[1:])):
        spacing = func(i, n)
        r2.top = r1.bottom + spacing

def makerect(**kwargs):
    rect = pygame.Rect(0, 0, 0, 0)
    for key, value in kwargs.items():
        setattr(rect, key, value)
    return rect

def get_bounding(rects):
    lefts, tops, rights, bottoms = zip(*map(getbounds, rects))
    left = min(lefts)
    top = min(tops)
    right = max(rights)
    bottom = max(bottoms)
    return pygame.Rect(left, top, right - left, bottom - top)

def movegroup(rects, **kwargs):
    old = get_bounding(rects)
    new = old.copy()
    for key, value in kwargs.items():
        setattr(new, key, value)
    dx = new.x - old.x
    dy = new.y - old.y
    for rect in rects:
        rect.x += dx
        rect.y += dy

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)

    pattern_func = pattern_functions[args.pattern]

    buffer = pygame.Surface((320, 240))
    space = buffer.get_rect()
    screen = pygame.display.set_mode((640, 240*4))
    window = screen.get_rect()
    clock = pygame.time.Clock()

    lane = Lane(
        target = makerect(size=(60, 70), midbottom=space.midbottom),
        notes = [
            Note(
                key = random.choice([pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]),
                rect = makerect(size=(40, 40), y=space.top * -i * 50),
            ) for i in range(100)
        ]
    )

    vertically_spaced = AlignmentKey('bottom', 'top', 80)
    align(lane.rects, vertically_spaced)
    movegroup(lane.rects, bottom=space.top, centerx=lane.target.centerx)

    for note in lane.notes:
        note.velocity = pygame.Vector2(0, 3)

    elapsed = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                current_note = lane.current
                if event.key == current_note.key:
                    if lane.target.contains(current_note.rect):
                        # Success
                        current_note.velocity.update(5, 0)
                    else:
                        current_note.velocity.update(-5, 0)

        # Move rects in lanes down.
        for note in lane.notes:
            note.rect.move_ip(note.velocity)

        buffer.fill('black')

        pygame.draw.rect(buffer, 'blue', lane.target, 1)
        for note in lane.notes:
            if note is lane.current:
                color = 'yellow'
            else:
                color = 'brown'
            note.draw(buffer, color)

        pygame.transform.scale(buffer, window.size, screen)
        pygame.display.update()

        elapsed = clock.tick(60)

def _main(argv=None):
    # Test drawing arrows
    parser = argument_parser()
    args = parser.parse_args(argv)

    pattern_func = pattern_functions[args.pattern]

    buffer = pygame.Surface((320, 240))
    space = buffer.get_rect()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()

    rect = makerect(size=(100, 100), center=space.center)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        buffer.fill('black')
        pygame.draw.polygon(buffer, 'red', list(right_arrow(rect)), 1)

        pygame.transform.scale(buffer, (640, 480), screen)
        pygame.display.update()

        elapsed = clock.tick(60)

if __name__ == '__main__':
    main()
