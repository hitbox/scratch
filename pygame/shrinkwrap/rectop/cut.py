from . import get
from .external import pygame

def position(pos, rect):
    """
    Subdivide rect at position `pos`.
    """
    if not rect.collidepoint(pos):
        return
    x, y = pos
    leftwidth = x - rect.x
    rightwidth = rect.right - x
    topheight = y - rect.y
    bottomheight = rect.bottom - y
    rects = [
        pygame.Rect(rect.x, rect.y, leftwidth, topheight),
        pygame.Rect(x, rect.y, rightwidth, topheight),
        pygame.Rect(rect.x, y, leftwidth, bottomheight),
        pygame.Rect(x, y, rightwidth, bottomheight),
    ]
    rects = [rect for rect in rects if rect.width > 0 and rect.height > 0]
    return rects

def with_knife(knife, rect):
    """
    Cut rect `rect` with rect `knife` returning a list of rects.
    """
    # TODO:
    # allow any cut, ie: remove test with clip
    # test for what `knife` is and cut appropriately.
    subrects = []
    knife = knife.clip(rect)
    if knife != rect:
        top_height = knife.top - rect.top
        left_width = knife.left - rect.left
        right_width = rect.right - knife.right
        bottom_height = rect.bottom - knife.bottom
        subrects = [
            # upper-left
            pygame.Rect(rect.topleft, (left_width, top_height)),
            # mid-upper
            pygame.Rect((knife.left, rect.top), (knife.width, top_height)),
            # upper-right
            pygame.Rect((knife.right, rect.top), (right_width, top_height)),
            # mid-right
            pygame.Rect((knife.right, knife.top), (right_width, knife.height)),
            # bottom-right
            pygame.Rect((knife.right, knife.bottom), (right_width, bottom_height)),
            # mid-bottom
            pygame.Rect((knife.left, knife.bottom), (knife.width, bottom_height)),
            # bottom-left
            pygame.Rect((rect.left, knife.bottom), (left_width, bottom_height)),
            # mid-left
            pygame.Rect((rect.left, knife.top), (left_width, knife.height)),
        ]
        # remove zero size rects
        # TODO: what happens in negative cartesian space?
        subrects = [rect for rect in subrects if rect.width > 0 and rect.height > 0]
    return subrects

def all(knife, rect_list):
    """
    """
    touching = [rect for rect in rect_list if rect.colliderect(knife)]
    all_subrects = [subrect for touched in touching for subrect in with_knife(knife, touched)]
    for rect in touching:
        rect_list.remove(rect)
    rect_list.extend(all_subrects)
