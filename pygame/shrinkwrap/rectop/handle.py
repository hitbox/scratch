from . import get
from . import resize
from . import util
from .external import pygame

MINSIZE = 25
MAXSIZE = 50

class Resizer:

    def __init__(self, rect):
        """
        :param rect: target rect to resize by dragging handles.
        """
        self.rect = rect
        # we position and resize later, constantly
        self.handle_rects = [pygame.Rect(0,0,0,0) for _ in get.POINTS]
        self.handles = dict(zip(get.POINTS, self.handle_rects))
        self.attribute_from_rect = {
            id(handlerect): pointname for pointname,handlerect in self.handles.items()
        }
        self.update_handles()

    def attribute_name_for_handle(self, handlerect):
        """
        Name for point on rect that handlerect is dragging.
        """
        return self.attribute_from_rect[id(handlerect)]

    def drag_by(self, handlerect, rel):
        # attribute name we need to move handle and resize rect
        dragattr = self.attribute_name_for_handle(handlerect)
        # fix up rel pos so handle moves properly
        rel = resize.handlerel(dragattr, rel)
        handlerect.move_ip(*rel)
        # resize rect according to how it was dragged
        resize.by_handle(self.rect, dragattr, rel)
        #
        self.update_handles()

    def update_handles(self):
        # position and resize handles on rect
        for attr, handle in self.handles.items():
            size = size_for_attr(attr, self.rect)
            byattr = get.opposite_point(attr)
            handle.size = size
            setattr(handle, byattr, getattr(self.rect, attr))

    def hover_rect(self):
        return self.rect.unionall(list(self.handles.values()))


def corner_size(rect):
    """
    """
    corner_size = min(rect.size) // 3
    corner_size = util.limit(corner_size, MINSIZE, MAXSIZE)
    corner_size = (corner_size,)*2
    return corner_size

def size_for_attr(attr, rect):
    """
    """
    square = corner_size(rect)
    if 'mid' not in attr:
        size = square
    elif 'top' in attr or 'bottom' in attr:
        size = (rect.width, square[1])
    elif 'left' in attr or 'right' in attr:
        size = (square[0], rect.height)
    return size

def make_handles(rect):
    """
    Make rects for the handles of another rect.
    """
    for attr, point in get.namedpoints(rect):
        size = size_for_attr(attr, rect)
        opposite_attr = get.opposite_point(attr)
        handle = get.new(size=size, **{opposite_attr: point})
        yield handle

def namedhandles(rect):
    """
    """
    for attr, point in get.namedpoints(rect):
        size = size_for_attr(attr, rect)
        handle = pygame.Rect((0,0), (0,0))
        yield (attr, handle)
