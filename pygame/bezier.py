import argparse
import contextlib
import itertools as it
import math
import operator as op
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

rect_corners = op.attrgetter('topleft', 'topright', 'bottomright', 'bottomleft')

class samples:

    def __init__(self, samples, time=0, speed=1):
        self.samples = samples
        self.time = time
        self.speed = speed

    def current(self):
        return self.time / self.samples

    def update(self):
        self.time = (self.time + self.speed) % self.samples


def clamp(x, a, b):
    if x < a:
        return a
    elif x > b:
        return b
    return x

def bezier(control_points, t):
    degree = len(control_points) - 1
    position = pygame.Vector2()
    for index, point in enumerate(control_points):
        coefficient = math.comb(degree, index) * (1-t)**(degree-index) * t**index
        position += point * coefficient
    return position

def bezier_tangent(control_points, t):
    # rewrite of above
    degree = len(control_points) - 1
    delta = pygame.Vector2()
    for index, (p1, p2) in enumerate(it.pairwise(control_points)):
        coefficient = (
            (degree * (p2 - p1))
            *
            math.comb(degree-1, index)
            *
            (1 - t)**(degree-1-index) * t**index
        )
        delta += coefficient
    return delta

def run():
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 60
    font = pygame.font.SysFont('monospace', 20)

    control_rect = window.inflate((-300,)*2)
    control_points = list(map(pygame.Vector2, rect_corners(control_rect)))
    control_radius = 10
    nsamples = 24
    point_samples = samples(500)

    line_points = None

    def update_line_points():
        nonlocal line_points
        line_points = [bezier(control_points, t/nsamples) for t in range(nsamples+1)]

    update_line_points()

    dragging = None
    running = True
    while running:
        elapsed = clock.tick(framerate)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # stop main loop
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    # keydown to quit
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # scroll to change number of samples of bezier line
                if event.button == pygame.BUTTON_WHEELDOWN:
                    if nsamples > 1:
                        nsamples -= 1
                        update_line_points()
                elif event.button == pygame.BUTTON_WHEELUP:
                    nsamples += 1
                    update_line_points()
            elif event.type == pygame.MOUSEBUTTONUP:
                # stop dragging
                dragging = None
            elif event.type == pygame.MOUSEMOTION:
                # begin or update dragging
                mouse_left, mouse_middle, mouse_right = event.buttons
                if mouse_left:
                    if dragging:
                        dragging.update(dragging + event.rel)
                        update_line_points()
                    else:
                        for control_point in control_points:
                            x = clamp(control_point[0], window.left, window.right)
                            y = clamp(control_point[1], window.top, window.bottom)
                            d = pygame.Vector2(event.pos).distance_to((x,y))
                            if d <= control_radius:
                                dragging = control_point
                                break
                        else:
                            dragging = None

        screen.fill('black')
        # draw first two and last two control points lines
        pygame.draw.lines(screen, 'grey', True, control_points[:2])
        pygame.draw.lines(screen, 'grey', True, control_points[-2:])

        # draw points moving along the curve
        point1 = bezier(control_points, point_samples.current())
        pygame.draw.circle(screen, 'coral', point1, 5)

        point2 = bezier(control_points, 1 - point_samples.current())
        pygame.draw.circle(screen, 'coral', point2, 5)

        # draw tangent
        tangent_vector = bezier_tangent(control_points, point_samples.current())
        pygame.draw.line(screen, 'blue', point1, tangent_vector + point1)

        point_samples.update()

        # draw control points as circles
        for center in control_points:
            x = clamp(center[0], window.left, window.right)
            y = clamp(center[1], window.top, window.bottom)
            pygame.draw.circle(screen, 'brown', (x,y), control_radius, 1)

        # draw bezier line
        pygame.draw.lines(screen, 'orange', False, line_points)

        # gui info
        items = [
            ('tangent_vector', tuple(f'{value:.2f}' for value in tangent_vector)),
            ('tangent_vector.magnitude()', f'{tangent_vector.magnitude():.2f}'),
            ('nsamples', nsamples),
        ]
        if False:
            for i, point in enumerate(control_points):
                items.append(
                    (f'control_points[{i}]', point)
                )
        keys, values = zip(*items)

        key_images = [font.render(str(thing), True, 'azure') for thing in keys]
        value_images = [font.render(str(thing), True, 'azure') for thing in values]

        key_rects = [image.get_rect() for image in key_images]
        for r1, r2 in it.pairwise(key_rects):
            r2.top = r1.bottom

        value_rects = [image.get_rect() for image in value_images]

        prev = None
        right = max(rect.right for rect in key_rects) + 10
        for rect in value_rects:
            rect.left = right
            if prev:
                rect.top = prev.bottom
            prev = rect

        pairs = it.chain(zip(key_images, key_rects), zip(value_images, value_rects))
        for image, rect in pairs:
            screen.blit(image, rect)

        pygame.display.flip()

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()
