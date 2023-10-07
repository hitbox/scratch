from .pygame import pygame

def border(surface, color, border_width):
    """
    Draw a border on a surface.
    """
    rect = surface.get_rect()
    topbottom = pygame.Rect((0,0), (rect.width, border_width))
    leftright = pygame.Rect((0,0), (border_width, rect.height))
    # left/right
    pygame.draw.rect(surface, color, leftright)
    leftright.right = rect.right
    pygame.draw.rect(surface, color, leftright)
    # top/bottom
    pygame.draw.rect(surface, color, topbottom)
    topbottom.bottom = rect.bottom
    pygame.draw.rect(surface, color, topbottom)
