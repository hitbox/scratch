from .pygame import pygame

class Engine:
    """
    Engine runs a state.
    """

    event_handler_attribute = 'event_handlers'

    def __init__(self, clock, screen, framerate=60):
        self.clock = clock
        self.screen = screen
        self.framerate = framerate
        self.running = False

    def run(self, state):
        self.running = True
        while self.running:
            self.update(state)

    def update(self, state):
        event_handlers = getattr(state, self.event_handler_attribute, {})
        elapsed = self.clock.tick(self.framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type in event_handlers:
                event_handlers[event.type](event)
        self.screen.clear()
        state.update(elapsed)
        self.screen.update()
