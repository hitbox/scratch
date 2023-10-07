from operator import ge
from operator import gt
from operator import le
from operator import lt

from . import get

class QueryError(Exception):
    pass


def is_above(rect1, rect2):
    return rect1.bottom < rect2.top

def is_below(rect1, rect2):
    return rect1.top > rect2.bottom

def is_between_horizontal(rect1, rect2):
    return rect1.right >= rect2.left and rect1.left <= rect2.right

def is_between_vertical(rect1, rect2):
    return rect1.top <= rect2.bottom and rect1.bottom >= rect2.top

def is_joinable(r1, r2):
    """
    Return whether two rects are joinable, ie: they are the same or they
    exactly share a side.
    """
    top1, right1, bottom1, left1 = get.sides(r1)
    top2, right2, bottom2, left2 = get.sides(r2)
    return (
        r1 == r2
        or (
            top1 == top2
            and bottom1 == bottom2
            and (right1 == left2 or left1 == right2)
        )
        or (
            left1 == left2
            and right1 == right2
            and (top1 == bottom2 or bottom1 == top2)
        )
    )

def is_leftof(rect1, rect2):
    return rect1.right < rect2.left

def is_rightof(rect1, rect2):
    return rect1.left > rect2.right

def predicate_getter(direction, test_rect):
    """
    Return predicate function to filter rect relationships.
    """
    is_between = is_between_predicate_map[direction]
    facing_predicate = facing_predicate_map[direction]

    def predicate(rect):
        return (
            facing_predicate(rect, test_rect)
            and is_between(rect, test_rect)
        )

    return predicate

def filter_rects(rects, direction, test):
    """
    Filter rects in relation to another rect.
    """
    predicate = predicate_getter(direction, test)
    return filter(predicate, rects)

facing_predicate_map = {
    'left': is_leftof,
    'right': is_rightof,
    'top': is_above,
    'bottom': is_below,
}

is_between_predicate_map = {
    'left': is_between_vertical,
    'right': is_between_vertical,
    'top': is_between_horizontal,
    'bottom': is_between_horizontal,
}
