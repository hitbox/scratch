import argparse
import contextlib
import itertools as it
import os
import random

from operator import attrgetter

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

colorfuls = list(it.product((255,0), repeat=3))

sides = attrgetter('top', 'right', 'bottom', 'left')

class RectDraw:

    def __init__(self, rect, **style):
        self.rect = rect
        self.style = style


def area(rect):
    return rect.width * rect.height

def get_rect(rect, **kwargs):
    "pygame.Surface.get_rect for pygame.Rect"
    rect = rect.copy()
    for key, value in kwargs.items():
        setattr(rect, key, value)
    return rect

def align(rects, attr1, attr2):
    "Set brect.attr1 to arect.attr2 pairwise"
    attr2 = attrgetter(attr2)
    for a, b in it.pairwise(rects):
        setattr(b, attr1, attr2(a))

def wrap(rects):
    "Bounding box of rects"
    sides = attrgetter('top', 'right', 'bottom', 'left')
    tops, rights, bottoms, lefts = zip(*map(sides, rects))
    top = min(tops)
    right = max(rights)
    bottom = max(bottoms)
    left = min(lefts)
    width = right - left
    height = bottom - top
    return pygame.Rect(left, top, width, height)

def moveas(rects, **kwargs):
    "Move rects as one"
    wrapped = wrap(rects)
    moved = get_rect(wrapped, **kwargs)
    dx = moved.x - wrapped.x
    dy = moved.y - wrapped.y
    for rect in rects:
        rect.x += dx
        rect.y += dy

def overlap(a, b):
    "Overlapping rect of a and b rects"
    # XXX
    # - unnecessary function
    # - use pygame.Rect.clip
    # - clip_from.clip(clip_to)
    _, left, right, _ = sorted([a.left, a.right, b.left, b.right])
    _, top, bottom, _ = sorted([a.top, a.bottom, b.top, b.bottom])
    width = right - left
    height = bottom - top
    return pygame.Rect(left, top, width, height)

def random_point(rect):
    top, right, bottom, left = sides(rect)
    return (
        random.randint(left, right),
        random.randint(top, bottom)
    )

def random_rect(inside):
    top, right, bottom, left = sides(inside)
    _left, _right = sorted(random.randint(left, right) for _ in range(2))
    _top, _bottom = sorted(random.randint(top, bottom) for _ in range(2))
    width = _right - _left
    height = _bottom - _top
    return (_left, _top, width, height)

def is_position_event(event):
    return (
        (
            event.type == pygame.MOUSEMOTION
            and
            event.buttons[0]
        )
        or
        (
            event.type == pygame.MOUSEBUTTONDOWN
            and
            event.button == pygame.BUTTON_LEFT
        )
    )

def iter_overlaps(rect, others):
    for other_rect in others:
        if other_rect is not rect and other_rect.colliderect(rect):
            yield (other_rect, other_rect.clip(rect))

def run(args):
    "Interactive overlapping rect demo"
    pygame.font.init()
    monofont = pygame.font.SysFont('monospace', 16)
    clock = pygame.time.Clock()
    fps = 60
    screen = pygame.display.set_mode((800,)*2)
    background = screen.copy()
    frame = screen.get_rect()
    side = min(frame.size)//4
    spawn = frame.inflate((-side,)*2)

    help_lines = (
        'Left click to set position',
        'Space rotate',
        'A/Z increase/decrease rects',
        'Escape or Q to quit',
    )
    images = [monofont.render(line, True, 'azure') for line in help_lines]
    rects = [image.get_rect() for image in images]
    align(rects, 'top', 'bottom')
    moveas(rects, bottomright=frame.bottomright)
    for image, rect in zip(images, rects):
        background.blit(image, rect)

    knife = RectDraw(
        pygame.Rect((0,)*2, (200,100)),
        color='magenta',
    )
    knife.rect.center = pygame.mouse.get_pos()

    nrects = 2
    draw_rects = []
    random.shuffle(colorfuls)
    colors = it.cycle(colorfuls)

    def genrects():
        draw_rects.clear()
        draw_rects.append(knife)
        while len(draw_rects) < nrects:
            for _ in range(10):
                rect = pygame.Rect(random_rect(spawn))
                if not any(rect.colliderect(draw_rect.rect) for draw_rect in draw_rects):
                    color = next(colors)
                    draw_rect = RectDraw(rect, color=color)
                    draw_rects.append(draw_rect)
                    break
            else:
                draw_rects.pop()

    genrects()
    frame = 0
    running = True
    while running:
        if args.output:
            filename = args.output.format(frame)
            if os.path.exists(filename):
                raise ValueError('output filename exists')
            pygame.image.save(screen, filename)
            frame += 1
        elapsed = clock.tick(fps)
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif event.key == pygame.K_SPACE:
                    # rotate
                    knife.rect.size = (knife.rect.height, knife.rect.width)
                    knife.rect.center = pygame.mouse.get_pos()
                elif event.key == pygame.K_a:
                    nrects += 1
                    genrects()
                elif event.key == pygame.K_z:
                    if nrects > 2:
                        nrects -= 1
                        genrects()
            elif is_position_event(event):
                knife.rect.center = event.pos
        # draw
        screen.blit(background, (0,)*2)

        # draw rects and collect overlaps

        overlapping = []
        for draw_rect in draw_rects:
            color = draw_rect.style.get('color', 'magenta')
            border = draw_rect.style.get('border', 1)
            pygame.draw.rect(screen, color, draw_rect.rect, border)
            if draw_rect.rect is not knife.rect and knife.rect.colliderect(draw_rect.rect):
                overlap = draw_rect.rect.clip(knife.rect)
                overlapping.append((draw_rect, overlap))

        # draw overlaps sorted smallest area last
        def overlap_area(item):
            _, overlaprect = item
            return area(overlaprect)

        for draw_rect, rect in sorted(overlapping, key=overlap_area, reverse=True):
            color1 = pygame.Color(knife.style.get('color', 'magenta'))
            color2 = pygame.Color(draw_rect.style.get('color', 'magenta'))
            color = color1.lerp(color2, 0.5)
            pygame.draw.rect(screen, color, rect, 0)
        pygame.display.flip()

def main(argv=None):
    "Draw overlapping rects"
    parser = argparse.ArgumentParser(
        description = main.__doc__,
    )
    parser.add_argument(
        '--output',
        help = 'Format string for frame output.',
    )
    args = parser.parse_args(argv)
    run(args)

if __name__ == '__main__':
    main()
