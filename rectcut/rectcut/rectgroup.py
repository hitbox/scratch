import itertools

from . import cutlib
from .types import CutType

class RectGroup:
    """
    Contains a list of rects.
    """

    def __init__(self, *rects):
        self.rects = list(rects)
        self.preview = None
        self.slicedirs = itertools.cycle(CutType)
        self.slicedir = next(self.slicedirs)

    def cutrect(self, pos):
        """
        Cut the rect colliding with position `pos`.
        """
        x, y = map(int, pos)
        cut = None
        for rect in self.rects:
            if rect.collidepoint((x,y)):
                if x in (rect.left, rect.right-1):
                    # possible drag
                    pass
                elif y in (rect.top, rect.bottom-1):
                    # possible drag
                    pass
                else:
                    cut = rect
                    break
        if cut:
            self.rects.remove(cut)
            a, b = cutlib.cutrect(cut, self.slicedir, pos)
            self.rects.append(a)
            self.rects.append(b)

    def update_preview(self, pos):
        x, y = map(int, pos)
        for rect in self.rects:
            if rect.collidepoint(pos):
                # NOTE: the right and bottom of a Rect is one pixel beyond
                # where the rect is drawn.
                if x in (rect.left, rect.right-1):
                    # possible drag
                    pass
                elif y in (rect.top, rect.bottom-1):
                    # possible drag
                    pass
                else:
                    self.preview = cutlib.cutrectline(rect, self.slicedir, pos)
                    break
        else:
            self.preview = None

    def switchdir(self):
        self.slicedir = next(self.slicedirs)
