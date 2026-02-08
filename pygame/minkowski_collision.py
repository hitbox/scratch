import argparse
import contextlib
import math
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class Circle:

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius


def distance_point_to_segment(point, seg_a, seg_b):
    ap = point - seg_a
    ab = seg_b - seg_a
    t = ap.dot(ab) / ab.length_squared()
    closest = seg_a + ab * t
    return (point - closest).length(), closest

def segment_circle_intersection(p1, p2, center, radius):
    x1, y1 = p1
    x2, y2 = p2
    cx, cy = center

    dx = x2 - x1
    dy = y2 - y1

    fx = x1 - cx
    fy = y1 - cy

    a = dx*dx + dy*dy
    b = 2 * (fx*dx + fy*dy)
    c = fx*fx + fy*fy - radius*radius

    discriminant = b*b - 4*a*c

    if discriminant < 0:
        return []  # no intersection

    discriminant = math.sqrt(discriminant)

    if a != 0:
        t1 = (-b - discriminant) / (2*a)
        t2 = (-b + discriminant) / (2*a)

        intersections = []

        if 0 <= t1 <= 1:
            intersections.append((x1 + t1*dx, y1 + t1*dy))

        if 0 <= t2 <= 1 and discriminant != 0:
            intersections.append((x1 + t2*dx, y1 + t2*dy))

        return intersections

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    screen = pygame.display.set_mode((800, 600))
    pygame.font.init()
    font = pygame.font.SysFont(None, 24)

    clock = pygame.time.Clock()

    # Moving circle (the swept shape)
    move_start = pygame.Vector2(100, 300)
    move_end   = pygame.Vector2(700, 320)

    moving = Circle(pygame.Vector2(0,0), radius=25)

    # Static obstacle
    obstacle = Circle(pygame.Vector2(450, 330), radius=40)

    # Minkowski-expanded obstacle (configuration space)
    minkowski_radius = moving.radius + obstacle.radius

    intersections = []
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                move_start.update(event.pos)

        screen.fill('black')

        move_end = pygame.Vector2(pygame.mouse.get_pos())

        # Path of the moving circle's center
        pygame.draw.line(screen, 'gray', move_start, move_end, 2)

        # Original obstacle
        pygame.draw.circle(screen, 'red', obstacle.center, obstacle.radius)

        # one or more intersections of line segment and circle
        intersections = segment_circle_intersection(move_start, move_end, obstacle.center, minkowski_radius)
        if intersections:
            # Moving circle placed at first intersection with inflated obstacle.
            pygame.draw.circle(screen, 'blue', intersections[0], moving.radius, 2)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
