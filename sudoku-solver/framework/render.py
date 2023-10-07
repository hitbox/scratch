# idea behind render vs draw being that render returns a surface and draw,
# draws on a surface.
from . import draw
from . import style
from .pygame import pygame

# ok, how about this styling thing? it accepts an argument for the name to
# lookup or defaults to itself.

def box(style_name=None):
    """
    """
    if style_name is None:
        style_name = f'{__name__}.box'
    size = style.get(style_name, 'size', (0,)*2)
    surface = pygame.Surface(size, flags=pygame.SRCALPHA)
    background_color = style.get(style_name, 'background.color')
    if background_color:
        surface.fill(background_color)
    border_color = style.get(style_name, 'border.color')
    if border_color:
        border_width = style.get(style_name, 'border.width', 1)
        draw.border(surface, border_color, border_width)
    # XXX:
    # * allow margins?
    return surface
