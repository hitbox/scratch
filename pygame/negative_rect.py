import argparse
import contextlib
import itertools as it
import operator as op
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

sides = op.attrgetter('top', 'right', 'bottom', 'left')

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

class Engine:

    def __init__(self):
        self.running = False

    def run(self, state):
        state.start(engine=self)
        self.running = True
        while self.running:
            state.update()

    def stop(self):
        self.running = False


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
        self.walls = list(surrounding(self.space))

        refrect = self.space.inflate((-min(self.space.size)//1.25,)*2)
        refrect.normalize()

        self.draggables = [refrect.copy()]
        self.dragging = None

    def update(self):
        # update
        margins = list(map(
            pygame.Rect,
            filter(
                lambda other: validate_inside(other, self.space),
                margin_rects(self.draggables, self.space)
            )
        ))
        # create labels
        text_blits = []
        for rect, color in zip(margins, COLORS):
            text = f'{rect.width}x{rect.height}={area(rect):,}'
            image = self.font.render(text, True, color)
            rect = image.get_rect(center=rect.center)
            text_blits.append((image, rect))
        # separate text labels
        rects = list(rect for _, rect in text_blits)
        resolve_overlaps(rects, self.walls, 100)
        # drawing
        self.clear()
        draw_rects(self.buffer, it.repeat('lime'), self.walls, width=0)
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
            event_name = pygame.event.event_name(event.type)
            method_name = f'do_{event_name.lower()}'
            method = getattr(self, method_name, None)
            if method is not None:
                method(event)
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
        screen_rel = event.rel
        delta = pygame.Vector2(*map(lambda x: x / self.scale, screen_rel))
        if not self.constraint_margins:
            self.dragging.topleft += delta
        else:
            # validate new position for margin area size
            testrect = pygame.Rect(self.dragging.topleft + delta, self.dragging.size)
            _margins = map(pygame.Rect, margin_rects([testrect], self.space))
            # all areas > x and there are valid margin rects all around
            valid_move = all(
                validate_inside(rect, self.space) and area(rect) > 1000
                for rect in _margins
            )
            if valid_move:
                self.dragging.topleft += delta

    def clear(self):
        self.buffer.fill('black')


def make_rect(rect=None, **kwargs):
    if rect is None:
        rect = pygame.Rect((0,)*4)
    else:
        rect = rect.copy()
    for key, val in kwargs.items():
        setattr(rect, key, val)
    return rect

def rect_from_points(x1, y1, x2, y2):
    w = x2 - x1
    h = y2 - y1
    return (x1, y1, w, h)

def aggsides(func, *rects):
    """
    execute `func` on all sides of all rects returning unpackable of
    `func(tops), func(rights), func(bottoms), func(lefts)`
    """
    return map(func, *map(sides, rects))

def minsides(*rects):
    """
    minimum of all four rects' sides
    """
    return aggsides(min, *rects)

def maxsides(*rects):
    """
    maximum of all four rects' sides
    """
    return aggsides(max, *rects)

def iter_rect_diffs(rect, inside):
    _, minright, minbottom, _ = minsides(rect, inside)
    maxtop, _, _, maxleft = maxsides(rect, inside)
    # topleft
    yield rect_from_points(*inside.topleft, *rect.topleft)
    # top
    yield rect_from_points(maxleft, inside.top, minright, rect.top)
    # topright
    yield rect_from_points(minright, inside.top, inside.right, rect.top)
    # right
    yield rect_from_points(minright, maxtop, inside.right, minbottom)
    # bottomright
    yield rect_from_points(*rect.bottomright, *inside.bottomright)
    # bottom
    yield rect_from_points(maxleft, rect.bottom, minright, inside.bottom)
    # bottomleft
    yield rect_from_points(inside.left, rect.bottom, rect.left, inside.bottom)
    # left
    yield rect_from_points(inside.left, maxtop, rect.left, minbottom)

def surrounding(rect):
    yield make_rect(size=rect.size, bottomright=rect.topleft)
    yield make_rect(size=rect.size, midbottom=rect.midtop)
    yield make_rect(size=rect.size, bottomleft=rect.topright)
    yield make_rect(size=rect.size, midleft=rect.midright)
    yield make_rect(size=rect.size, topleft=rect.bottomright)
    yield make_rect(size=rect.size, midtop=rect.midbottom)
    yield make_rect(size=rect.size, topright=rect.bottomleft)
    yield make_rect(size=rect.size, midright=rect.midleft)

def validate_inside(rect, inside):
    _, _, w, h = rect
    return 0 < w < inside.width and 0 < h < inside.height

def margin_rects(rects, inside):
    for rect in rects:
        for other in iter_rect_diffs(rect, inside):
            yield other

def area(rect):
    return rect.width * rect.height

def overlapping(rects):
    for r1, r2 in it.combinations(rects, 2):
        if r1.colliderect(r2):
            yield (r1, r2)

def resolve_overlaps(rects, immovable, maxsteps):
    for _ in range(maxsteps):
        overlaps = [
            (r1, r2) for r1, r2 in overlapping(rects)
        ]
        if not overlaps:
            break
        for r1, r2 in overlaps:
            if r1 in immovable and r2 in immovable:
                continue
            elif r1 in immovable:
                resolve_from_immovable(r2, r1)
            elif r2 in immovable:
                resolve_from_immovable(r1, r2)
            else:
                delta = pygame.Vector2(r1.center) - r2.center
                overlap = pygame.Vector2(r1.clip(r2).size)
                delta.scale_to_length(overlap.length())
                r1.center += delta / 2
                r2.center -= delta / 2

def resolve_from_immovable(rect, immovable):
    """
    Move rect outside of the immovable rect.
    """
    overlap = rect.clip(immovable)
    if overlap.width > 0 and overlap.height > 0:
        dx, dy = overlap.size
        if dx < dy:
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
    parser.add_argument('--size', type=size_type, default='320 240')
    parser.add_argument('--scale', type=int, default='2')
    args = parser.parse_args(argv)

    width, height = args.size

    pygame.font.init()
    screen = pygame.display.set_mode((width*args.scale, height*args.scale))

    state = Demo(args.scale, FRAMERATE, 18)
    engine = Engine()
    engine.run(state)

if __name__ == '__main__':
    main()
