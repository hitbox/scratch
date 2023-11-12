from abc import ABC
from abc import abstractmethod

import lib
import rectop

from lib.external import pygame

class Tool(ABC):
    """
    GUI Tool. This is the layer between the GUI and the actual rect operation.
    """

    @abstractmethod
    def reset(self):
        """
        Make tool ready to begin.
        """

    @abstractmethod
    def on_event(self, event):
        """
        Each tool handles any event.
        """


class RectTool(Tool):
    """
    Generic drag out a rect tool.
    """

    def __init__(self):
        self.event_dispatch = {
            lib.event.DRAGSTART: self.on_dragstart,
            lib.event.DRAGMOTION: self.on_dragmotion,
            lib.event.DRAGDROP: self.on_dragdrop,
        }

    def reset(self):
        self.selection = None

    def on_event(self, event):
        """
        Dispatch event to handler.
        """
        if event.type in self.event_dispatch:
            self.event_dispatch[event.type](event)

    def on_dragstart(self, event):
        """
        On drag start, begin new rect.
        """
        self.selection = pygame.Rect(event.start, (0,0))

    def on_dragmotion(self, event):
        """
        On drag (mouse) motion, resize new rect.
        """
        pressed = pygame.key.get_pressed()
        is_square = pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]

        x1, y1 = event.start
        x2, y2 = event.pos

        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if is_square:
            length = min([width, height])
            x2 = x1 + length
            y2 = y1 + length

        rectop.get.normalized(event.start, (x2, y2), rect=self.selection)


class NewRectTool(RectTool):
    """
    Create a new rect tool.
    """
    def __init__(self, new_rect_callback):
        super().__init__()
        self.new_rect_callback = new_rect_callback

    def on_dragdrop(self, event):
        """
        On (drag) drop, create new rect from selection rect.
        """
        self.new_rect_callback(self.selection)
        self.reset()


class RectsGetterTool(RectTool):
    """
    Apply some operation on selected rects.
    """

    def __init__(
        self,
        rects_getter,
    ):
        super().__init__()
        self.rects_getter = rects_getter


class CutRectTool(RectsGetterTool):
    """
    Cut rects with a selection rect.
    """

    def on_dragdrop(self, event):
        """
        Cut colliding rects on drop.
        """
        rectop.cut.all(self.selection, self.rects_getter())
        self.reset()


class DefragRectTool(RectsGetterTool):
    """
    Defrag (join) rects inside selection.
    """

    def __init_(self, rects_getter):
        super().__init__(rects_getter)
        self.event_dispatch[pygame.MOUSEBUTTONDOWN] = self.on_mousebuttondown

    def _defrag(self):
        rects = self.rects_getter()
        result = rectop.join.defrag(rects)
        rectop.join.apply(result, rects)
        self.reset()

    def on_mousebuttondown(self, event):
        self._defrag()

    def on_dragdrop(self, event):
        """
        Defrag all rects regardless of selection.
        """
        self._defrag()


class SelectTool(RectsGetterTool):
    """
    Select rects tool.
    """

    def __init__(
        self,
        rects_getter,
        selected_callback,
        unselected_callback,
    ):
        super().__init__(rects_getter)
        self.selected_callback = selected_callback
        self.unselected_callback = unselected_callback
        self.event_dispatch[pygame.MOUSEBUTTONDOWN] = self.on_mousebuttondown

    def on_mousebuttondown(self, event):
        """
        """
        rects = self.rects_getter()
        for rect in rects:
            if rect.collidepoint(event.pos):
                self.selected_callback(rect)

    def on_dragdrop(self, event):
        """
        On (drag) drop, notify of selected and unselected.
        """
        rects = self.rects_getter()
        for rect in rects:
            if self.selection.contains(rect):
                self.selected_callback(rect)
            else:
                self.unselected_callback(rect)
        self.reset()


class DeleteTool(RectsGetterTool):

    def __init__(self, rects_getter):
        super().__init__(rects_getter)
        self.hover = set()
        self.event_dispatch[pygame.MOUSEMOTION] = self.on_mousemotion
        self.event_dispatch[pygame.MOUSEBUTTONDOWN] = self.on_mousebuttondown

    def on_mousemotion(self, event):
        rects = self.rects_getter()
        self.hover = set(id(rect) for rect in rects if rect.collidepoint(event.pos))

    def on_mousebuttondown(self, event):
        """
        """
        rects = self.rects_getter()
        for rect in list(rects):
            if rect.collidepoint(event.pos):
                rects.remove(rect)
        self.reset()

    def on_dragdrop(self, event):
        """
        On (drag) drop, notify of selected and unselected.
        """
        if self.selection:
            rects = self.rects_getter()
            for rect in list(rects):
                if self.selection.contains(rect):
                    rects.remove(rect)
            self.reset()


class SubdivideTool(RectsGetterTool):
    """
    Click point inside rect and split it into four rects.
    """

    def __init__(self, rects_getter):
        super().__init__(rects_getter)
        self.hover = None
        self.event_dispatch[pygame.MOUSEMOTION] = self.on_mousemotion
        self.event_dispatch[pygame.MOUSEBUTTONDOWN] = self.on_mousebuttondown

    def on_mousemotion(self, event):
        rects = self.rects_getter()
        for rect in rects:
            if rect.collidepoint(event.pos):
                self.hover = id(rect)
                break
        else:
            self.hover = None

    def do_subdivide(self, event):
        """
        """
        if self.hover:
            rects = self.rects_getter()
            for rect in list(rects):
                if id(rect) == self.hover:
                    pos = event.pos
                    pos = rect.center
                    subdivided_rects = rectop.cut.position(pos, rect)
                    rects.remove(rect)
                    rects.extend(subdivided_rects)
                    break
            else:
                # uh oh
                pass
        self.reset()

    def on_mousebuttondown(self, event):
        """
        """
        self.do_subdivide(event)

    def on_dragdrop(self, event):
        """
        Eat this event
        """


class IntersetRectTool(RectsGetterTool):
    """
    The intersection of two rects.
    """

    def __init__(
        self,
        rects_getter,
        new_rect_callback,
    ):
        super().__init__(rects_getter)
        self.new_rect_callback = new_rect_callback

    def on_dragdrop(self, event):
        """
        """
        rects = self.rects_getter()
        selected = [rect for rect in rects if self.selection.contains(rect)]
        if len(selected) == 2:
            irect = rectop.get.intersection(*selected)
            if irect:
                self.new_rect_callback(irect)
                for rect in selected:
                    rects.remove(rect)
        self.reset()
