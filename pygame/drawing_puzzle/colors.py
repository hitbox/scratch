import argparse
import contextlib
import itertools as it
import math
import os
import random

from operator import attrgetter

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

def is_colorful(color):
    color = pygame.Color(color)
    hue, saturation, lightness, alpha = color.hsla
    return (
        30 < saturation <= 100
        and
        20 < lightness < 60
    )

def get_rect(rect=None, **kwargs):
    if rect is None:
        result = pygame.Rect((0,)*4)
    else:
        result = rect.copy()
    for key, val in kwargs.items():
        setattr(result, key, val)
    return result

def square_grid_rows(n_items):
    # rows as main axis
    rows = math.ceil(math.sqrt(n_items))
    columns = math.ceil(n_items / rows)
    return (rows, columns)

def square_grid_cols(n_items):
    # columns as main axis
    columns = math.ceil(math.sqrt(n_items))
    rows = math.ceil(n_items / columns)
    return (rows, columns)

def generate_grid_rects(iterable, size, ncols, offset=None, gap=0):
    # TODO
    # - by row, as in give argument nrows?
    if offset is None:
        offset = (0,)*2
    ox, oy = offset
    width, height = size
    for index, _ in enumerate(iterable):
        j, i = divmod(index, ncols)
        x = ox + i * width + gap
        y = oy + j * height + gap
        rect = pygame.Rect(x, y, width, height)
        yield rect

def wrap_rects(rects):
    rect, *rects = rects
    return rect.unionall(rects)

def move_as_group(rects, **kwargs):
    origin = wrap_rects(rects)
    dest = get_rect(origin, **kwargs)
    delta = pygame.Vector2(dest.topleft) - origin.topleft
    for rect in rects:
        rect.topleft += delta

def eliminate_by_predicate(items, predicate, r=2):
    eliminated = set()
    for item1, item2 in it.combinations(items, r=r):
        if not predicate(item1, item2):
            eliminated.add(item1)
            eliminated.add(item2)
    yield from (item for item in items if item not in eliminated)

def slope(line):
    (x1, y1), (x2, y2) = line
    run = (x2 - x1)
    if run == 0:
        return math.inf
    rise = (y2 - y1)
    return rise / run

def shaded_rect_lines(rect, step):
    xs = range(rect.left, rect.right + step, step)
    ys = range(rect.top, rect.bottom + step, step)
    for (x, y) in zip(xs, ys):
        x = min(rect.right, x)
        y = min(rect.bottom, y)
        line = ((rect.left, y), (x, rect.top))
        yield line

    xs = range(rect.right, rect.left, -step)
    ys = range(rect.bottom, rect.top, -step)
    for (x, y) in zip(xs, ys):
        x = min(rect.right, x)
        y = min(rect.bottom, y)
        line = ((x, rect.bottom), (rect.right, y))
        yield line

def shaded_rect_lines(rect, line, step):
    (x1, y1), (x2, y2) = line
    for x in range(rect.left, rect.right, step):
        yield ((x1 + x, y1), (min(x2 + x, rect.right), y2))

def color_from_hsla(h, s, l, a=1.0):
    color = pygame.Color((255,)*3)
    color.hsla = (h, s, l, a)
    return color

def set_lightness(color, l):
    color = pygame.Color(color)
    h, s, _, a = color.hsla
    color.hsla = (h, s, l, a)
    return color

def set_hue(color, h):
    color = pygame.Color(color)
    _, s, l, a = color.hsla
    color.hsla = (h, s, l, a)
    return color

def hsl_distance(c1, c2):
    c1, c2 = map(pygame.Color, [c1,c2])
    h1, s1, l1, _ = c1.hsla
    h2, s2, l2, _ = c2.hsla
    return pygame.Vector3(h1, s2, l1).distance_to((h2, s2, l2))

def generate_colors_by_hsl_distance(colors):
    def hsl_distance_predicate(item1, item2):
        return hsl_distance(item1, item2) > 3
    colorful_colors = set(filter(is_colorful, colors))
    return colorful_colors

def generate_colors_by_elimination(colors):
    return set(eliminate_by_predicate(colors, hsl_distance_predicate))

def rgb_distance(color1, color2):
    # chatgpt
    # Simple Euclidean distance in RGB color space
    # square root of the sum of the squared differences of the rgb components
    return sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)) ** 0.5

def generate_visually_distinct_colors(num_colors):
    # chatgpt
    base_colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (0, 255, 255),
        (255, 0, 255),
    ]
    colors = base_colors[:min(num_colors, len(base_colors))]

    # Generate additional colors based on distance
    while len(colors) < num_colors:
        # Average of existing colors
        new_color = (int(sum(c) / len(colors)) for c in zip(*colors))
        new_color = tuple(int(c) for c in new_color)

        # Check if new color has sufficient distance from existing colors
        if all(rgb_distance(new_color, existing_color) > 100 for existing_color in colors):
            colors.append(new_color)

    return colors[:num_colors]

def example_visually_distinct():
    # Example usage:
    number_of_colors = 8
    distinct_colors = generate_visually_distinct_colors(number_of_colors)

    print("Visually distinct colors:")
    for color in distinct_colors:
        print(color)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    colors = [color_from_hsla(hue, 100, 50) for hue in range(0, 360, 5)]

    nrows, ncols = square_grid_cols(len(colors))
    # there are at least as many cells as colors
    assert ncols * nrows >= len(colors)

    window = pygame.Rect((0,)*2, (800,)*2)
    area_width, area_height = (value * 0.75 for value in window.size)

    width = area_width // ncols
    height = area_height // nrows
    rects = list(generate_grid_rects(colors, (width, height), ncols, gap=1))
    image = pygame.Surface((area_width, area_height))

    rect = None
    def update():
        nonlocal rect
        for rect, color in zip(rects, colors):
            pygame.draw.rect(image, color, rect)
            other_color = set_hue(color, (color.hsla[0] + 180) % 360)
            pygame.draw.rect(image, other_color, rect, 2)
            pygame.draw.circle(image, other_color, rect.center, min(rect.size)//8)
        rect = image.get_rect(center = window.center)

    update()

    def render():
        screen.fill('black')
        screen.blit(image, rect)
        pygame.display.flip()

    screen = pygame.display.set_mode(window.size)
    clock = pygame.time.Clock()
    framerate = 60
    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif event.key == pygame.K_r:
                    # randomize colors
                    random.shuffle(colors)
                    update()
                    render()
                elif event.key == pygame.K_s:
                    # sort colors by hue
                    colors.sort(key=lambda c: c.hsla[0])
                    update()
                    render()
            elif event.type == pygame.WINDOWEXPOSED:
                render()

if __name__ == '__main__':
    main()

