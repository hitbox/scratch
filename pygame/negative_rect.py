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

    def __init__(self, scale, framerate, fontsize):
        self.scale = scale
        self.framerate = framerate
        self.fontsize = fontsize
        self.clock = pygame.time.Clock()

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
        self.walls = [
            make_rect(self.space, bottom=self.space.top),
            make_rect(self.space, left=self.space.right),
            make_rect(self.space, top=self.space.bottom),
            make_rect(self.space, right=self.space.left),
        ]

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
            pygame.draw.rect(self.buffer, color, rect, 1)
            text = f'{rect.width}x{rect.height}={rect.width*rect.height}'
            image = self.font.render(text, True, 'azure')
            rect = image.get_rect(center=rect.center)
            text_blits.append((image, rect))
        # separate text labels
        while True:
            rects = list(rect for _, rect in text_blits)
            rects += self.walls
            if not any(r1.colliderect(r2) for r1, r2 in it.combinations(rects, 2)):
                break
            for r1, r2 in it.combinations(rects, 2):
                if r1.colliderect(r2):
                    overlap = pygame.Vector2(r1.clip(r2).size)
                    if r1 in self.walls:
                        r2.topleft -= overlap
                    elif r2 in self.walls:
                        r1.topleft -= overlap
                    else:
                        r1.topleft -= overlap / 2
                        r2.topleft += overlap / 2
        # drawing
        self.clear_screen()
        self.draw_draggables()
        self.draw_margins(margins)
        # draw text labels
        for (image, rect), color in zip(text_blits, COLORS):
            pygame.draw.circle(self.buffer, color, rect.center, 2)
            self.buffer.blit(image, rect)
        # scale and update display
        pygame.transform.scale(self.buffer, self.window.size, self.screen)
        pygame.display.flip()
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
        delta = pygame.Vector2(*map(lambda x: x / self.scale, event.rel))
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

    def clear_screen(self):
        self.buffer.fill('black')

    def draw_walls(self):
        for rect in self.walls:
            pygame.draw.rect(self.buffer, 'lime', rect, 1)

    def draw_draggables(self):
        for rect in self.draggables:
            pygame.draw.rect(self.buffer, 'purple4', rect, 1)

    def draw_margins(self, margins):
        for rect, color in zip(margins, COLORS):
            pygame.draw.rect(self.buffer, color, rect, 1)


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
    return map(func, *map(sides, rects))

def minsides(*rects):
    return aggsides(min, *rects)

def maxsides(*rects):
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

def validate_inside(rect, inside):
    _, _, w, h = rect
    return 0 < w < inside.width and 0 < h < inside.height

def margin_rects(rects, inside):
    for rect in rects:
        for other in iter_rect_diffs(rect, inside):
            yield other

def area(rect):
    return rect.width * rect.height

def size_type(string):
    return tuple(map(int, string.replace(',', ' ').split()))

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
