from . import get
from . import util

MINHANDLE = 20

BOTH = (1, 1)
ONLYX = (1, 0)
ONLYY = (0, 1)

# 0 or 1 masks for "handles" of a rect, ordered same as POINTS
HANDLE_POINTS_REL_MASKS = [
    ONLYY, # midtop
    BOTH,  # topright
    ONLYX, # midright
    BOTH,  # bottomright
    ONLYY, # midbottom
    BOTH,  # bottomleft
    ONLYX, # midleft
    BOTH,  # topleft
]

NAMED_HANDLE_POINTS_REL_MASKS = dict(zip(get.POINTS, HANDLE_POINTS_REL_MASKS))

def by_handle(rect, attr, rel):
    """
    In-place resize and move rect as if it is being manipulated by one of its
    handles, i.e.: rect points.

    :param rect: rect to resize and move by a handle.
    :param attr: name of rect attribute to drag rect by.
    :param rel: x/y to move handle by.
    """
    dx, dy = rel
    if attr == 'topright':
        rect.width += dx
        rect.y += dy
        rect.height -= dy
    elif attr == 'bottomright':
        rect.width += dx
        rect.height += dy
    elif attr == 'bottomleft':
        rect.x += dx
        rect.width -= dx
        rect.height += dy
    elif attr == 'topleft':
        rect.x += dx
        rect.y += dy
        rect.width -= dx
        rect.height -= dy
    elif 'mid' in attr:
        if 'top' in attr:
            rect.y += dy
            rect.height -= dy
        elif 'bottom' in attr:
            rect.height += dy
        elif 'right' in attr:
            rect.width += dx
        elif 'left' in attr:
            rect.x += dx
            rect.width -= dx
    rect.normalize()

def handlerel(attr, rel):
    """
    Modify relative position (change) `rel` so that the attribute `attr` is
    moved appropriately.
    """
    cantype = type(rel)
    mask = NAMED_HANDLE_POINTS_REL_MASKS[attr]
    return cantype(a*b for a,b in zip(mask,rel))

def update_handle_for_rect(rect, hrects, exclude=None):
    # need to use exclude instead of externally filtered list so that the
    # indexes of points and handle rects and such line up.
    if exclude is None:
        exclude = []
    d = 4
    corner_size = ( util.limit(min(rect.size) // d, MINHANDLE, MINHANDLE), ) * 2
    horizontal_size = (rect.width // d, MINHANDLE)
    vertical_size = (MINHANDLE, rect.height // d)
    for attr, hrect in zip(get.POINTS, hrects):
        if hrect in exclude:
            continue
        # size
        if 'mid' not in attr:
            size = corner_size
        elif 'top' in attr or 'bottom' in attr:
            size = horizontal_size
        elif 'left' in attr or 'right' in attr:
            size = vertical_size
        hrect.size = size
        # position
        opposite_attr = get.opposite_point(attr)
        setattr(hrect, opposite_attr, getattr(rect, attr))
