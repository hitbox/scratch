from .pygame import pygame

def connect_events(obj, prefix='on_'):
    """
    Return dictionary of event callbacks by inspecting `obj` for methods with
    `prefix`.
    """
    callbacks = {}
    for name in dir(obj):
        if name.startswith(prefix):
            event_name = name[len(prefix):].upper()
            event = getattr(pygame, event_name)
            callbacks[event] = getattr(obj, name)
    return callbacks

def post_quit():
    pygame.event.post(pygame.event.Event(pygame.QUIT))
