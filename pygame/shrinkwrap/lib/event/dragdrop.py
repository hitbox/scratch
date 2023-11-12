"""
Add support for a DRAG and DRAGDROP event to pygame.

Call lib.event.for_drag(event) in your event processor.
"""
from ..external import pygame

# TODO
# Clean this up and put it in its own module.

DRAGSTART = pygame.event.custom_type()
DRAGMOTION = pygame.event.custom_type()
DRAGDROP = pygame.event.custom_type()

__drag = None
__was_dragged = False

def is_drop(event):
    """
    This event was a drop, after dragging (moving).
    """
    return (
        event.type == pygame.MOUSEBUTTONUP
        and event.button == pygame.BUTTON_LEFT
        and __drag
        and __was_dragged
    )

def is_drag_update(event):
    """
    Drag button is down and mouse is moving.
    """
    return (
        event.type == pygame.MOUSEMOTION
        and event.buttons[0]
        and __drag
    )

def is_drag_start(event):
    """
    Just drag button down, setup possible drag-(move-)drop.
    """
    return (
        event.type == pygame.MOUSEBUTTONDOWN
        and event.button == pygame.BUTTON_LEFT
        and __drag is None
        and not __was_dragged
    )

def for_drag(event):
    """
    Call this is your event processor to emit drag-start, drag-update, and
    drag-drop events.
    """
    global __drag
    global __was_dragged

    if is_drop(event):
        drop = pygame.event.Event(DRAGDROP,
            name = 'DRAGDROP',
            start = __drag.start,
            pos = event.pos,
        )
        pygame.event.post(drop)
        __drag = None
        __was_dragged = False

    elif is_drag_update(event):
        __was_dragged = True
        __drag = pygame.event.Event(
            DRAGMOTION,
            name = 'DRAGMOTION',
            start = __drag.start,
            pos = event.pos,
            rel = event.rel,
        )
        __drag.pos = event.pos
        pygame.event.post(__drag)

    elif is_drag_start(event):
        __drag = pygame.event.Event(
            DRAGSTART,
            name = 'DRAGSTART',
            start = event.pos,
            pos = event.pos,
        )
        pygame.event.post(__drag)
