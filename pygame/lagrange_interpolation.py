import argparse
import contextlib
import os

from itertools import pairwise

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class CopyAttr:

    def __init__(self, from_attr, to_attr):
        self.from_attr = from_attr
        self.to_attr = to_attr

    def __call__(self, obj1, obj2):
        setattr(obj2, self.to_attr, getattr(obj1, self.from_attr))


left_top_to_bottom = CopyAttr(
    from_attr = 'bottomleft',
    to_attr = 'topleft',
)

def point_type(string):
    return tuple(map(int, string.replace(',', ' ').split()))

def l_i(x, i, points):
    xi, _ = points[i]
    result = 1
    for j, (xj, _) in enumerate(points):
        if j != i:
            result *= (x - xj) / (xi - xj)
    return result

def p(x, points):
    total = 0
    for i, (_, yi) in enumerate(points):
        total += yi * l_i(x, i, points)
    return total

def floatrange(start, end, step):
    yield float(start)
    while start < end:
        start += step
        yield start

def main(argv=None):
    """
    Lagrange interpolation demonstration with pygame.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--points', nargs='+', type=point_type, default=list())
    parser.add_argument('--step', default=0.1, type=float)
    args = parser.parse_args(argv)

    screen = pygame.display.set_mode((800, 600))
    frame = screen.get_rect()
    pygame.font.init()
    font = pygame.font.SysFont(None, 24)

    background = screen.copy()
    lines = [
        'Lagrange Interpolation Demonstration',
        'Right-click to clear points.',
        'Left-click to place point.',
    ]
    text_images = [font.render(line, True, 'azure') for line in lines]
    text_rects = [image.get_rect() for image in text_images]

    text_rects[0].topright = frame.topright
    for r1, r2 in pairwise(text_rects):
        left_top_to_bottom(r1, r2)

    for image, rect in zip(text_images, text_rects):
        background.blit(image, rect)

    points = args.points

    if points:
        xmin = min(x for x, _ in points)
        xmax = max(x for x, _ in points)
        interpolated_points = [
            (x, p(x, points))
            for x in floatrange(xmin, xmax, args.step)
        ]
    else:
        interpolated_points = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_RIGHT:
                    points.clear()
                    interpolated_points.clear()
                elif event.button == pygame.BUTTON_LEFT:
                    points.append(event.pos)
                    x_values = [x for x, _ in points]
                    xmin = min(x_values)
                    xmax = max(x_values)
                    interpolated_points = [
                        (x, p(x, points))
                        for x in floatrange(xmin, xmax, args.step)
                    ]

        # Draw
        screen.blit(background, (0,0))

        # draw original points
        for point in points:
            pygame.draw.circle(screen, 'brown', point, 10)

        # draw interpolated points
        if len(interpolated_points) > 1:
            pygame.draw.lines(screen, 'azure', False, interpolated_points)

        pygame.display.flip()


if __name__ == '__main__':
    main()
