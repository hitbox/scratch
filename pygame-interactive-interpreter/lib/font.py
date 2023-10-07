from abc import ABC
from abc import abstractmethod

from lib.external import pygame

class BaseFont(ABC):

    @abstractmethod
    def render(self, text):
        pass


class PygameFont(BaseFont):
    """
    Wrap pygame.font.Font with some conveniences.
    """

    impl = pygame.font.Font
    fallback_impl = pygame.font.SysFont

    def __init__(self, font, size, antialias=True):
        self.size = size
        self.antialias = antialias
        self._update_font(font)

    def _update_font(self, font):
        try:
            self._font = self.impl(font, self.size)
        except FileNotFoundError:
            self._font = self.fallback_impl(font, self.size)

    def render(self, text, color=None):
        if color is None:
            color = (200, ) * 3
        return self._font.render(text, self.antialias, color)

    def render_lines(self, lines, color=None):
        raise NotImplementedError
