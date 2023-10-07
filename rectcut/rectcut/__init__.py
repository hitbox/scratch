import itertools

from . import cutlib
from .display import ScaledDisplay
from .engine import Engine
from .pygame import pygame
from .states import RectCutState
from .types import CutType

def run():
    """
    Start rect cutter main loop.
    """
    pygame.display.init()
    rect = pygame.Rect(0, 0, 100, 100)
    screen = ScaledDisplay((8*rect.width, 8*rect.height), rect.size)
    clock = pygame.time.Clock()
    engine = Engine(clock, screen)
    initial_rect = rect.inflate(-rect.width*.25, -rect.width*.25)
    state = RectCutState(engine, initial_rect)
    engine.run(state)
