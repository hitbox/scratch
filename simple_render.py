import argparse
import contextlib
import itertools as it
import math
import os

from operator import attrgetter

right_angle = math.pi / 2

with open(os.devnull, 'w') as devnull:
    with contextlib.redirect_stdout(devnull):
        import pygame

del devnull

class GameRect:
    """
    """
    rect_point_attrs = ['topleft', 'topright', 'bottomright', 'bottomleft']
    get_rect_points = attrgetter(*rect_point_attrs)

    def __init__(self, points):
        self.points = list(points)
        assert len(self.points) == 4

    @classmethod
    def from_rect(cls, *rect_args):
        rect = pygame.Rect(*rect_args)
        return cls(cls.get_rect_points(rect))

    @property
    def is_rectangle(self):
        pairs = it.pairwise(it.chain(self.points, [self.points[0]]))
        return all(is_straight(p1, p2) for p1, p2 in pairs)

    @property
    def as_rect(self):
        # XXX
        # - Got to here and this is quickly becoming careful management of
        #   attributes.
        # - For what benefit?
        # - Just always draw polygons, if they're going to rotate and scale and
        #   such?
        # - The benefit that rects will be fast?
        self._rect = pygame.


def is_horizonal(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return y1 == y2 and x1 != x2

def is_vertical(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return x1 == x2 and y1 != y2

def is_straight(p1, p2):
    return is_horizonal(p1, p2) or is_vertical(p1, p2)

def demo():
    """
    """
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    frames_per_second = 60

    gamerect = GameRect.from_rect(0, 0, 100, 100)
    print(gamerect.is_rectangle)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        screen.fill('black')
        if gamerect.is_straight:
            pygame.draw.rect(screen, 'olive', gamerect.)
        pygame.display.flip()

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    demo()

if __name__ == '__main__':
    main()
