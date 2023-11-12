import unittest

from lib.external import pygame
from lib.rectutil import iterpoints
from lib.rectutil import rect_from_points

class TestCase(unittest.TestCase):

    def setUp(self):
        self.rect = pygame.Rect(10,15,30,25)

    def test_iterpoints(self):
        a = list(iterpoints(self.rect))
        b = [
            (10+15, 15), # midtop
            (10+30, 15), # topright
            (10+30, 15+25//2), # midright
            (10+30, 15+25), # bottomright
            (10+15, 15+25), # midbottom
            (10, 15+25), # bottomleft
            (10, 15+25//2), # midleft
            (10, 15), # topleft
        ]
        self.assertEqual(a, b)

    def test_rect_from_points(self):
        points = [(10,15),(40,15+25)]
        rect = rect_from_points(points)
        self.assertEqual(rect, self.rect)


if __name__ == '__main__':
    unittest.main()
