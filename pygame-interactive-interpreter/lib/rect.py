from itertools import tee

from lib.external import pygame

def wraprects(rects):
    """
    Stretch a rect around `rects` like a rubber band.
    """
    a, b, c, d = tee(rects, 4)
    left = min((rect.left for rect in a), default=0)
    top = min((rect.top for rect in b), default=0)
    right = max((rect.right for rect in c), default=0)
    bottom = max((rect.bottom for rect in d), default=0)
    rect = pygame.Rect(left, top, right - left, bottom - top)
    return rect
