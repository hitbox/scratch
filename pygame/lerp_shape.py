import argparse
import contextlib
import math
import os

from itertools import pairwise

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

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

def main(argv=None):
    """
    Lerp animation of a circle around a rect.
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    pygame.font.init()
    font = pygame.font.SysFont(None, 25)
    screen = pygame.display.set_mode((800, 600))
    frame = screen.get_rect()

    clock = pygame.time.Clock()

    shape = frame.inflate((-300, -300))
    points = list(star_outline_points(frame.centerx, frame.centery, 250, 100))
    segments = list(pairwise(points)) + [(points[-1], points[0])]

    t = 0
    s = 0.018
    width_delta = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    s += 0.0005
                elif event.key == pygame.K_DOWN:
                    s -= 0.0005
        t += s
        if t > 1:
            t = 0
        t_eased = ease_in_out_quad(t)

        if width_delta != 0:
            shape.width += width_delta
            if shape.width < 100:
                width_delta *= -1
            if shape.width > 600:
                width_delta *= -1
            shape.center = frame.center

        # Updates for lerping around rect.
        lengths = [math.dist(p1, p2) for p1, p2 in segments]
        total_length = sum(lengths)

        cum_lengths = [0]
        for length in lengths:
            clen = cum_lengths[-1] + length / total_length
            cum_lengths.append(clen)

        # Draw
        screen.fill('black')
        for i in range(len(segments)):
            cl1 = cum_lengths[i]
            cl2 = cum_lengths[(i+1) % len(cum_lengths)]
            p1 = segments[i][0]
            p2 = segments[i][1]
            if cl1 <= t_eased < cl2:
                local_t = (t_eased - cl1) / (cl2 - cl1)
                pos = lerp2d(p1, p2, local_t)
                pygame.draw.line(screen, 'brown', p1, pos, 1)
                pygame.draw.circle(screen, 'white', pos, 5, 0)
                break
            else:
                pygame.draw.line(screen, 'brown', p1, p2, 1)

        lines = [
            f'{t=:0.2f}',
            f'{t_eased=:0.2f}',
            f'{s=:0.5f}',
        ]
        images = [font.render(line, True, 'azure') for line in lines]
        rects = [image.get_rect() for image in images]
        for r1, r2 in zip(rects, rects[1:]):
            r2.topleft = r1.bottomleft
        for image, rect in zip(images, rects):
            screen.blit(image, rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
