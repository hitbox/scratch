import pygame

import core
import base

class View(base.Base):

    rect_color = None

    # sprites draw themselves on views
    # views draw themselves on whatever the Core provides
    # scenes provide views for sprites to draw themselves on

    def __init__(self, position=None, rect=None, lens=None, background=None):
        # NOTE: added position when I tried moving views around. I wanted a
        #       subpixel way to do that. And then I added repositioning the
        #       lens to x, y in the update method.
        if position is None:
            position = (0., 0.)
        self.x, self.y = position
        # =====================================================================
        # rect is where to draw the view on the screen
        if rect is None:
            rect = core.Core.get_apparent_screen_rect()
        self.rect = rect
        # =====================================================================
        # lens is the rect sprites will use for their purposes of drawing
        # themselves
        if lens is None:
            lens = core.Core.get_apparent_screen_rect()
        self.lens = lens
        # surface is the pygame.surface sprites should draw themselves on
        self.surface = pygame.Surface(self.lens.size)
        # =====================================================================
        if background is None:
            background = pygame.Color(0,0,0)
        self.background = background

    def draw(self, surface):
        dirty_rect = surface.blit(self.surface, self.rect)
        if self.rect_color is not None:
            pygame.draw.rect(surface, self.rect_color, self.rect, 1)
        return dirty_rect

    def update(self):
        self.lens.topleft = int(self.x), int(self.y)

    def clear(self):
        #TODO: allow background to be an image?
        self.surface.fill(self.background)


