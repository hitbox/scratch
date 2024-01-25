import argparse
import itertools as it

import pygamelib

from pygamelib import pygame

COLORS = [
    'brown',
    'olive',
    'orchid',
    'orange',
    'turquoise',
    'purple',
    'salmon',
    'olivedrab',
    'teal',
]

FRAMERATE = 60

class Demo:

    def __init__(self, scale, framerate, fontsize, constraint_margins=False):
        self.scale = scale
        self.framerate = framerate
        self.fontsize = fontsize
        self.clock = pygame.time.Clock()
        self.constraint_margins = constraint_margins

    def start(self, engine):
        self.engine = engine
        self.screen = pygame.display.get_surface()
        self.window = self.screen.get_rect()
        self.size = self.screen.get_size()
        self.font = pygame.font.SysFont('monospace', self.fontsize)

        size = tuple(map(lambda x: x / self.scale, self.window.size))
        self.buffer = pygame.Surface(size)
        self.world = self.buffer.get_rect()
        self.space = self.world.inflate((-min(self.world.size)//3,)*2)
        self.walls = list(pygamelib.rectwalls(self.space))

        refrect = self.space.inflate((-min(self.space.size)//1.25,)*2)
        refrect.normalize()

        self.draggables = [refrect.copy()]
        self.dragging = None

    def update(self):
        # update
        margins = list(map(
            pygame.Rect,
            filter(self.space.contains,
               filter(bool, # neither dimension is zero
                  margin_rects(self.draggables, self.space)))
        ))
        # create labels
        text_blits = []
        for rect, color in zip(margins, COLORS):
            text = f'{rect.width}x{rect.height}={pygamelib.area(rect):,}'
            image = self.font.render(text, True, color)
            rect = image.get_rect(center=rect.center)
            text_blits.append((image, rect))
        # separate text labels
        rects = [rect for _, rect in text_blits]
        resolve_overlaps(rects, self.walls, 100)
        # drawing
        self.clear()
        draw_rects(self.buffer, it.repeat('mediumpurple4'), self.walls, width=0)
        draw_rects(self.buffer, it.repeat('purple4'), self.draggables, width=1)
        draw_rects(self.buffer, COLORS, margins, width=1)
        # draw text labels
        for (image, rect), color in zip(text_blits, COLORS):
            pygame.draw.circle(self.buffer, color, rect.center, 2)
            self.buffer.blit(image, rect)
        # scale and update display
        pygame.transform.scale(self.buffer, self.window.size, self.screen)
        pygame.display.flip()
        # events
        for event in pygame.event.get():
            pygamelib.dispatch(self, event)
        self.clock.tick(self.framerate)

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def do_mousebuttonup(self, event):
        self.dragging = None

    def do_mousebuttondown(self, event):
        world_pos = map(lambda x: x / self.scale, event.pos)
        for rect in self.draggables:
            if rect.collidepoint(*world_pos):
                self.dragging = rect
                break
        else:
            self.dragging = None

    def do_mousemotion(self, event):
        if not (event.buttons[0] and self.dragging):
            return
        # left button down and moving
        delta = pygame.Vector2(*map(lambda x: x / self.scale, event.rel))
        self.dragging.topleft += delta

    def clear(self):
        self.buffer.fill('black')


def margin_rects(rects, inside):
    for rect in rects:
        yield from pygamelib.iter_rect_diffs(rect, inside)

def resolve_overlaps(rects, immovable, maxsteps):
    for _ in range(maxsteps):
        overlaps = list(pygamelib.overlaps(rects + immovable))
        if not overlaps:
            break
        for r1, r2, overlap in overlaps:
            if r1 in immovable and r2 in immovable:
                continue
            elif r1 in immovable:
                resolve_from_immovable(r2, r1, overlap)
            elif r2 in immovable:
                resolve_from_immovable(r1, r2, overlap)
            else:
                delta = pygame.Vector2(overlap.size)
                r1.center += delta / 2
                r2.center -= delta / 2

def resolve_from_immovable(rect, immovable, overlap):
    """
    Move rect outside of the immovable rect.
    """
    if overlap.height > overlap.width:
        if rect.centerx < immovable.centerx:
            rect.right = immovable.left
        else:
            rect.left = immovable.right
    else:
        if rect.centery < immovable.centery:
            rect.bottom = immovable.top
        else:
            rect.top = immovable.bottom

def draw_rects(surf, colors, rects, **kwargs):
    for color, rect in zip(colors, rects):
        pygame.draw.rect(surf, color, rect, **kwargs)

def size_type(string):
    size = tuple(map(int, string.replace(',', ' ').split()))
    if len(size) < 2:
        size *= 2
    return size

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=size_type, default='800')
    parser.add_argument('--scale', type=int, default='1')
    args = parser.parse_args(argv)

    width, height = args.size

    pygame.font.init()
    screen = pygame.display.set_mode((width*args.scale, height*args.scale))

    state = Demo(args.scale, FRAMERATE, 18)
    engine = pygamelib.Engine()
    engine.run(state)

if __name__ == '__main__':
    main()
