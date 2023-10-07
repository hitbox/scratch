from .pygame import pygame

class Display:
    """
    Normal display.
    """

    def __init__(self, screensize, modeargs=None):
        self.screensize = screensize
        self.modeargs = modeargs
        if self.modeargs is None:
            self.modeargs = dict()
        self._surface = pygame.display.set_mode(self.screensize, **self.modeargs)
        self._background = self._surface.copy()

    @property
    def surface(self):
        return self._surface

    @property
    def background(self):
        return self._background

    def toscreen(self, x, y):
        return (x, y)

    def tospace(self, x, y):
        return (x, y)

    def clear(self):
        self._surface.blit(self._background, (0,0))

    def update(self):
        pygame.display.flip()


class ScaledDisplay(Display):
    """
    Scaled display.
    """

    def __init__(self, screensize, buffersize, modeargs=None):
        super().__init__(screensize, modeargs)
        self.buffersize = buffersize
        self._buffer = pygame.Surface(self.buffersize)
        self._buffer_initial = self._buffer.copy()

        sw, sh = screensize
        bw, bh = buffersize
        self.xscale = sw // bw
        self.yscale = sh // bh

    @property
    def surface(self):
        return self._buffer

    def tospace(self, x, y):
        return (x // self.xscale, y // self.yscale)

    def toscreen(self, x, y):
        raise NotImplementedError
        return (x, y)

    def clear(self):
        self._buffer.blit(self._buffer_initial, (0, 0))

    def update(self):
        pygame.transform.scale(self._buffer, self.screensize, self._surface)
        pygame.display.flip()
