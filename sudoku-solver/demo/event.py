from framework.pygame import pygame

class EventHandler:

    def __init__(self):
        pass

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.on_keydown(event)
        elif event.type == pygame.MOUSEMOTION:
            self.on_mousemotion(event)

    def on_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def on_mousemotion(self, event):
        # XXX: left off here. want something like the `style` module to hold
        # all game objects--I think.
        pass
