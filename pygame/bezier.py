import argparse
import contextlib
import itertools as it
import math
import operator as op
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

RECT_POINTS = [
    'topleft',
    'midtop',
    'topright',
    'midright',
    'bottomright',
    'midbottom',
    'bottomleft',
    'midleft',
]

RECT_CORNERS = [name for name in RECT_POINTS if 'mid' not in name]
rect_points = op.attrgetter(*RECT_POINTS)
rect_corners = op.attrgetter(*RECT_CORNERS)

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

def mix(x, a, b):
    return a * (1 - x) + b * x

def remap(x, a, b, c, d):
    return x*(d-c)/(b-a) + c-a*(d-c)/(b-a)

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

    control_rect = window.inflate((-500,)*2)
    control_points = list(map(pygame.Vector2, [
        control_rect.bottomleft,
        control_rect.midleft,
        control_rect.midtop,
        control_rect.topright,
    ]))
    constrain_points = [control_points[0], control_points[-1]]
    control_radius = 10
    nsamples = 24
    point_samples = samples(100)
    bezier_x = control_rect.left

    line_points = None

    _lerp_rect = window.inflate((-300,)*2)
    lerp_line = tuple(map(pygame.Vector2, (_lerp_rect.bottomleft, _lerp_rect.bottomright)))

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
                        new = dragging + event.rel
                        if dragging in constrain_points:
                            new.x = clamp(new.x, control_rect.left, control_rect.right)
                            new.y = clamp(new.y, control_rect.top, control_rect.bottom)
                        dragging.update(new)
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
        # draw points moving along the curve
        point1 = bezier(control_points, point_samples.current())
        pygame.draw.circle(screen, 'coral', point1, 5)
        rect = pygame.Rect((0,)*2, (20,)*2)
        rect.midtop = (point1.x, control_rect.bottom)
        pygame.draw.lines(screen, 'red', True, [rect.midtop, rect.bottomright, rect.bottomleft])

        # draw control points as circles
        pygame.draw.rect(screen, 'brown', control_rect, 1)

        # draw first two and last two control points lines
        pygame.draw.line(screen, 'grey', *control_points[:2])
        pygame.draw.line(screen, 'grey', *control_points[-2:])
        for center in control_points:
            if center in constrain_points:
                color = 'brown'
            else:
                color = 'magenta'
            pygame.draw.circle(screen, color, center, control_radius, 1)

        # draw bezier line
        pygame.draw.lines(screen, 'orange', False, line_points)

        # draw lerp line
        pygame.draw.line(screen, 'darkred', *lerp_line)
        bezier_y_t = remap(point1.y, control_rect.left, control_rect.right, 1, 0)
        centerx = mix(bezier_y_t, lerp_line[0].x, lerp_line[1].x)
        center = (centerx, lerp_line[0].y)
        pygame.draw.circle(screen, 'darkviolet', center, 10)

        # gui info
        items = [
            ('nsamples', nsamples),
        ]
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

        # weird place for updates
        point_samples.update()

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()
