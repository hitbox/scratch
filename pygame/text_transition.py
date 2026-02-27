import argparse
import colorsys
import contextlib
import math
import os
import random

from itertools import cycle

import numpy as np

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame
    import this

def rect_points(rect):
    yield rect.topleft
    yield rect.topright
    yield rect.bottomright
    yield rect.bottomleft

def rect_segments(rect):
    yield (rect.topleft, rect.topright)
    yield (rect.topright, rect.bottomright)
    yield (rect.bottomright, rect.bottomleft)
    yield (rect.bottomleft, rect.topleft)

def lerp(a, b, t):
    return a + t * (b - a)

def is_colorful(color):
    r, g, b, a = color
    r /= 255
    g /= 255
    b /= 255

    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    return s > 0.7 and v > 0.8

def render_text(font, text, antialias=True, color='azure', **rect_kwargs):
    image = font.render(text, True, color).convert_alpha()
    return image

def lerp_surface(s1, s2, t):
    a1 = pygame.surfarray.array3d(s1).astype(np.float32)
    a2 = pygame.surfarray.array3d(s2).astype(np.float32)

    blend = ((1-t)*a1 + t * a2).astype(np.uint8)
    result = pygame.surfarray.make_surface(blend)
    return result

def lerp_surface_scaled(s1, s2, t):
    # interpolate size
    w = int(lerp(s1.get_width(),  s2.get_width(),  t))
    h = int(lerp(s1.get_height(), s2.get_height(), t))
    size = (max(1, w), max(1, h))

    # scale both to same intermediate size
    s1_scaled = pygame.transform.smoothscale(s1, size)
    s2_scaled = pygame.transform.smoothscale(s2, size)

    # blend RGBA
    a1 = pygame.surfarray.pixels3d(s1_scaled).astype(np.float32)
    a2 = pygame.surfarray.pixels3d(s2_scaled).astype(np.float32)

    alpha1 = pygame.surfarray.pixels_alpha(s1_scaled).astype(np.float32)
    alpha2 = pygame.surfarray.pixels_alpha(s2_scaled).astype(np.float32)

    rgb = ((1 - t) * a1 + t * a2).astype(np.uint8)
    alpha = ((1 - t) * alpha1 + t * alpha2).astype(np.uint8)

    result = pygame.Surface(size, pygame.SRCALPHA)
    pygame.surfarray.blit_array(result, rgb)
    pygame.surfarray.pixels_alpha(result)[:] = alpha

    return result

def lerp2d(a, b, t):
    x1, y1 = a
    x2, y2 = b
    x = x1 * (1 - t) + x2*t
    y = y1 * (1 - t) + y2*t
    return (x, y)

def ease_in_out_quad(t):
    if t < 0.5:
        return 2 * t * t
    else:
        return -1 + (4 - 2*t) * t

def star_points(cx, cy, r, n):
    points = []
    for i in range(n):
        angle = math.tau * i / n - math.pi / 2  # start at top
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    return points

def star_outline_points(cx, cy, outer_r, inner_r, n=5):
    for i in range(n):
        angle_outer = 2*math.pi * i / n - math.pi/2
        x_outer = cx + outer_r * math.cos(angle_outer)
        y_outer = cy + outer_r * math.sin(angle_outer)
        yield (x_outer, y_outer)

        angle_inner = angle_outer + math.pi / n
        x_inner = cx + inner_r * math.cos(angle_inner)
        y_inner = cy + inner_r * math.sin(angle_inner)
        yield (x_inner, y_inner)

def starwise(points, skip=2):
    n = len(points)
    for i in range(n):
        p1 = points[i]
        p2 = points[(i + skip) % n]
        yield (p1, p2)

zen_text = "".join([this.d.get(c, c) for c in this.s])

def main(argv=None):
    """
    Lerp animation of a circle around a rect.
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    words = cycle(zen_text.split())

    colors = [color for color in pygame.color.THECOLORS.values() if is_colorful(color)]
    random.shuffle(colors)
    colors = cycle(colors)

    pygame.font.init()
    font = pygame.font.SysFont(None, 225)
    screen = pygame.display.set_mode((800, 600))
    frame = screen.get_rect()

    clock = pygame.time.Clock()

    transition = lerp_surface_scaled

    t = 0
    t_speed = 0.125
    image1 = render_text(font, next(words), color=next(colors))
    image2 = render_text(font, next(words), color=next(colors))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        t += t_speed
        if t >= 1:
            t = 0
            image1 = image2
            image2 = render_text(font, next(words), color=next(colors))

        word_image = transition(image1, image2, ease_in_out_quad(t))
        word_rect = word_image.get_rect(center=frame.center)

        # Draw
        screen.fill('black')
        screen.blit(word_image, word_rect)
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
