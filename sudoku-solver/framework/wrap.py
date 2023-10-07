from .pygame import pygame

def rects(rects):
    top = min(rect.top for rect in rects)
    right = max(rect.right for rect in rects)
    bottom = max(rect.bottom for rect in rects)
    left = min(rect.left for rect in rects)
    rect = pygame.Rect(left, top, right - left, bottom - top)
    return rect
