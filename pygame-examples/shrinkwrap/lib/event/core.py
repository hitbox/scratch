from collections import defaultdict

from ..external import pygame

ANYEVENT = pygame.event.custom_type()

registry = None

# XXX
# is this worth it's own module?

def reset():
    global registry
    registry = defaultdict(list)

def listen(event_type, func):
    """
    Register callable `func` to respond to events of type `event_type`.
    """
    registry[event_type].append(func)

def listen_for(event_type):
    """
    Decorator version of `listen`.
    """
    def decorator(func):
        listen(event_type, func)
    return decorator

def dispatch(event):
    """
    """
    for func in registry[ANYEVENT]:
        func(event)
    for func in registry[event.type]:
        func(event)

reset()
