from lib.external import pygame

class Screen:

    def __init__(self, size, flags=0, depth=0, display=0, vsync=0, background=None):
        self.surface = pygame.display.set_mode(size, flags, depth, display, vsync)
        if background is None:
            background = self.surface.copy()
        self.background = background
        self.rect = self.surface.get_rect()

    def blit(self, source, position):
        return self.surface.blit(source, position)

    def clear(self):
        self.surface.blit(self.background, (0,0))

    def update(self):
        pygame.display.flip()
