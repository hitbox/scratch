from .pygame import pygame
from .types import CutType

def cutrect(rect, slicedir, pos):
    """
    Cut rect returning two
    """
    x, y = pos
    if slicedir == CutType.VERTICAL:
        a = pygame.Rect(rect.topleft, (x-rect.left, rect.height))
        b = pygame.Rect(x, rect.top, rect.right - x, rect.height)
    elif slicedir == CutType.HORIZONTAL:
        a = pygame.Rect(rect.topleft, (rect.width, y - rect.top))
        b = pygame.Rect(rect.left, y, rect.width, rect.bottom - y)
    return (a, b)

def cutrectline(rect, slicedir, pos):
    """
    Preview line
    """
    x, y = pos
    if slicedir == CutType.VERTICAL:
        start, end = ((x, rect.top), (x, rect.bottom-1))
    elif slicedir == CutType.HORIZONTAL:
        start, end = ((rect.left, y), (rect.right-1, y))
    start, end = sorted([start, end])
    return start, end
