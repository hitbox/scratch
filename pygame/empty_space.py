import argparse
import itertools as it
import operator as op
import random

from pprint import pprint

import pygamelib

from pygamelib import pygame

COLORS = [
    'bisque',
    'brown',
    'burlywood',
    'chartreuse',
    'chocolate',
    'coral',
    'cornsilk',
    'crimson',
    'cyan',
    'firebrick',
    'gainsboro',
    'gold',
    'goldenrod',
    'hotpink',
    'indigo',
    'ivory',
    'khaki',
    'lavender',
    'lavenderblush',
    'lemonchiffon',
    'lime',
    'maroon',
    'mintcream',
    'moccasin',
    'navy',
    'olive',
    'olivedrab',
    'orange',
    'orchid',
    'palegoldenrod',
    'paleturquoise',
    'peachpuff',
    'peru',
    'pink',
    'plum',
    'rosybrown',
    'salmon',
    'saddlebrown',
    'sandybrown',
    'seashell',
    'sienna',
    'tan',
    'teal',
    'thistle',
    'tomato',
    'turquoise',
    'violet',
    'wheat',
    'yellow',
]

sides = op.attrgetter('top', 'right', 'bottom', 'left')

def find_empty_space(rectangles, inside):
    empties = [inside]
    for rect in rectangles:
        empties = list(map(pygame.Rect, subtract_rect(empties, rect)))
    return empties

def subtract_rect(empties, rect_to_subtract):
    for empty in empties:
        clip = empty.clip(rect_to_subtract)
        if not all(clip.size):
            # no intersection
            yield empty
            continue
        if empty.left < clip.left:
            # left rect
            yield (empty.left, empty.top, clip.left - empty.left, empty.height)
        if empty.right > clip.right:
            # right rect
            yield (clip.right, empty.top, empty.right - clip.right, empty.height)
        if empty.top < clip.top:
            # top rect
            minright = min(empty.right, clip.right)
            maxleft = max(empty.left, clip.left)
            yield (maxleft, empty.top, minright - maxleft, clip.top - empty.top)
        if empty.bottom > clip.bottom:
            # bottom rect
            minright = min(empty.right, clip.right)
            maxleft = max(empty.left, clip.left)
            yield (maxleft, clip.bottom, minright - maxleft, empty.bottom - clip.bottom)

def area(rect):
    return rect.width * rect.height

def rect_from_points(x1, y1, x2, y2):
    return (x1, y1, x2 - x1, y2 - x1)

def rand_rect_point(rect):
    top, right, bottom, left = sides(rect)
    return (random.randint(left, right), random.randint(top, bottom))

def rand_endpoints(inside):
    return (*rand_rect_point(inside), *rand_rect_point(inside))

def unionable(r1, r2):
    top1, right1, bottom1, left1 = sides(r1)
    top2, right2, bottom2, left2 = sides(r2)
    return (
        (top1 == bottom2 and r1.width == r2.width)
        or
        (right1 == left2 and r1.height == r2.height)
        or
        (bottom1 == top2 and r1.width == r2.width)
        or
        (left1 == right2 and r1.height == r2.height)
    )

def defrag_rects(r1, r2):
    if unionable:
        yield r1.union(r2)
    else:
        yield r1
        yield r2

def random_rect(inside):
    endpoints = rand_endpoints(inside)
    rect = pygame.Rect(rect_from_points(*endpoints))
    rect.normalize()
    return rect

def generate_random_rects(nrects):
    rects = set()
    while len(rects) < nrects:
        if not window.contains(rect):
            continue
        if (
            rect.width > 1
            and
            rect.height > 1
            and
            not any(other.colliderect(rect) for other in rects)
        ):
            rects.add(rect)
            yield rect

def defrag_rects(rects):
    while True:
        for r1, r2 in it.combinations(rects, 2):
            if unionable(r1, r2):
                rects.append(r1.union(r2))
                rects.remove(r1)
                rects.remove(r2)
                break
        else:
            # nothing unioned, stop trying
            break

def find_empty_space2(rects, inside):
    tops, rights, bottoms, lefts = zip(*map(sides, rects))

    tops += (inside.bottom,)
    rights += (inside.left,)
    bottoms += (inside.top,)
    lefts += (inside.right,)

    xsides = lefts + rights
    ysides = tops + bottoms

    def is_valid(rect):
        return (
            all(rect.size)
            and
            rect not in result
            and
            inside.contains(rect)
            and
            not any(rect.colliderect(other) for other in rects)
            and
            not any(
                negrect.contains(rect) or negrect.colliderect(rect)
                for negrect in result
            )
        )

    result = list()
    while True:
        negs = list()
        for x1, x2 in it.combinations(xsides, 2):
            for y1, y2 in it.combinations(ysides, 2):
                rect = pygame.Rect(rect_from_points(x1, y1, x2, y2))
                rect.normalize()
                if is_valid(rect):
                    negs.append(rect)
                rect = pygame.Rect(rect_from_points(x2, y2, x1, y1))
                rect.normalize()
                if is_valid(rect):
                    negs.append(rect)
        if not negs:
            break
        biggest = sorted(negs, key=area)[-1]
        result.append(biggest)
    return result

def run(rects, empty_space_rects):
    pygame.font.init()
    clock = pygame.time.Clock()
    framerate = 60
    font = pygame.font.SysFont('monospace', 20)
    screen = pygame.display.get_surface()
    window = screen.get_rect()

    colors = random.sample(COLORS, len(rects))
    i = 0
    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    i = (i - 1) % len(empty_space_rects)
                elif event.key == pygame.K_RIGHT:
                    i = (i + 1) % len(empty_space_rects)
                else:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        screen.fill('black')
        for rect, color in zip(rects, colors, strict=True):
            pygame.draw.rect(screen, color, rect, 0)
            image = font.render(f'{color}', True, 'black', 'white')
            screen.blit(image, image.get_rect(center=rect.center))

        highlight = empty_space_rects[i]
        pygame.draw.rect(screen, 'magenta', highlight, 0)
        image = font.render(f'{i=}/{len(empty_space_rects)-1}', True, 'white')
        rect = image.get_rect(topleft=highlight.topright).clamp(window)
        screen.blit(image, rect)
        pygame.display.flip()

def size_type(string):
    size = tuple(map(int, string.replace(',', ' ').split()))
    if len(size) < 2:
        size *= 2
    return size

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('--nrects', type=int, default=1)
    args = parser.parse_args(argv)

    if args.nrects > len(COLORS):
        parser.error('Invalid nrects')

    window = pygame.Rect((0,)*2, args.display_size)

    random.seed(0)
    rects = []
    while len(rects) < args.nrects:
        rect = random_rect(window)
        if (
            window.contains(rect)
            and
            not any(other.colliderect(rect) for other in rects)
        ):
            rects.append(rect)

    # negative rects
    empty_space_rects = list(find_empty_space(rects, window))
    assert empty_space_rects

    defrag_rects(empty_space_rects)
    empty_space_rects = sorted(empty_space_rects)

    pygame.display.set_mode(window.size)
    run(rects, empty_space_rects)

if __name__ == '__main__':
    main()
