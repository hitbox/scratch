import scenes

from lib.external import pygame

class StopEngine(Exception):
    pass


class Engine:

    def run(self, scene):
        scenes.switch(scene)
        running = True
        while running:
            # allow scenes to switch
            scene = scenes.update()
            try:
                events = pygame.event.get()
                scene.update(events)
            except StopEngine:
                running = False


def stopengine():
    raise StopEngine()
