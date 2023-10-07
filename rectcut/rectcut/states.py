import abc

from .events import connect_events
from .events import post_quit
from .pygame import pygame
from .rectgroup import RectGroup
from .types import CutType

class CutTypeError(Exception):
    """
    """


def cuttype_from_line(a, b):
    """
    Return CutType item from endpoints a and b.
    """
    x_equal = a[0] == b[0]
    y_equal = a[1] == b[1]
    if x_equal and y_equal:
        raise CutTypeError('Line endpoint are equal.')
    if x_equal:
        return CutType.VERTICAL
    else:
        return CutType.HORIZONTAL

class BaseState(metaclass=abc.ABCMeta):
    """
    Must inherit this to be run by an engine. Optional
    `Engine.event_handler_attribute` attribute is called to display all events
    except `pygame.QUIT`.
    """

    @abc.abstractmethod
    def update(self, elapsed):
        pass


class RectCutState(BaseState):
    """
    Demo cutting one big rect into littler ones.
    """

    def __init__(self, engine, initial_rect):
        self.engine = engine
        self.initial_rect = initial_rect
        self.rects = RectGroup(self.initial_rect)
        self.event_handlers = connect_events(self)
        pygame.font.init()
        self.font = pygame.font.Font(None, 12)

    def on_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            post_quit()

    def on_mousebuttondown(self, event):
        if event.button == pygame.BUTTON_LEFT:
            pos = self.engine.screen.tospace(*event.pos)
            self.rects.cutrect(pos)
        elif event.button == pygame.BUTTON_RIGHT:
            self.rects.switchdir()
            pos = self.engine.screen.tospace(*event.pos)
            self.rects.update_preview(pos)

    def on_mousemotion(self, event):
        pos = self.engine.screen.tospace(*event.pos)
        self.rects.update_preview(pos)
        # XXX
        # Left off here thinking about dragging again. Want to drag "connected"
        # rects too.

    def update(self, elapsed):
        self.draw()

    def draw(self):
        self.engine.screen.clear()
        self.draw_rects()
        if self.rects.preview:
            self.draw_preview_line()
        self.engine.screen.update()

    def draw_rects(self):
        screen = self.engine.screen
        # draw all rects
        for rect in self.rects.rects:
            pygame.draw.rect(screen.surface, (200,200,200), rect, 1)

    def draw_preview_line(self):
        screen = self.engine.screen
        a, b = self.rects.preview
        pygame.draw.line(screen.surface, (200,0,0), a, b)

    def draw_preview_magniture(self):
        # XXX: this is not useful. really want cross distance.
        screen = self.engine.screen
        cuttype = cuttype_from_line(a, b)
        linerect = pygame.Rect(a, (b[0] - a[0], b[1] - a[1]))
        if cuttype == CutType.HORIZONTAL:
            magnitude = abs(a[0] - b[0])
            position = dict(midbottom=linerect.center)
        else:
            magnitude = abs(a[1] - b[1])
            position = dict(midright=linerect.center)

        text = self.font.render(f'{magnitude}', True, (200,)*3)
        screen.surface.blit(text, text.get_rect(**position))
