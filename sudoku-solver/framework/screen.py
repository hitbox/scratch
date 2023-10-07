from .pygame import pygame

class Screen:

    def __init__(self, size, scale=1):
        self.size = size
        self.scale = scale
        if self.scale != 1:
            self._screen = pygame.display.set_mode(self.scaled_size())
            self._buffer = pygame.Surface(self.size)
            self._clear_buffer = self._buffer.copy()
            self.surface = self._buffer
            # * overlay does not exist if not scaled.
            # * a separate surface is needed because the smaller buffer will
            #   overwrite the screen surface.
            self.overlay = pygame.Surface(self.scaled_size(), flags=pygame.SRCALPHA)
            self.clear_overlay = self.overlay.copy()
            self.frame = self._screen.get_rect()
        else:
            self._screen = pygame.display.set_mode(self.size)
            self._clear_screen = self._screen.copy()
            self.surface = self._screen
            self.frame = self.surface.get_rect()
        self.rect = self.surface.get_rect()
        self.background = self._screen.copy()

    def clear(self):
        if self.scale != 1:
            self._buffer.blit(self._clear_buffer, (0,0))
            self.overlay.blit(self.clear_overlay, (0,0))
        else:
            self._screen.blit(self._clear_screen, (0,0))

    def scaled_size(self):
        width, height = self.size
        return (width * self.scale, height * self.scale)

    def update(self):
        if self.scale != 1:
            pygame.transform.scale(self._buffer, self.scaled_size(), self._screen)
            self._screen.blit(self.overlay, (0,0))
        pygame.display.flip()
