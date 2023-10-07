import sudoku

from framework.pygame import pygame
from framework.screen import Screen

from . import style as sudoku_style
from . import render as sudoku_render
from . import event as sudoku_event

class SudokuApp:
    """
    The main Sudoku GUI app.
    """

    def __init__(self, engine):
        self.engine = engine
        self.screen = None
        self.event_handler = sudoku_event.EventHandler()
        self.board = sudoku.new_board()
        self.guiboard = None
        self.board_renderer = None

    def start(self):
        sudoku_style.init()
        self.board_renderer = sudoku_render.BoardRenderer()
        self.screen = Screen((320, 200), scale=4)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.stop()
            else:
                self.event_handler.on_event(event)
            # separate object to handle events?
        # draw
        self.screen.clear()
        image = self.board_renderer.render(self.board)
        self.screen.surface.blit(image, image.get_rect(center=self.screen.rect.center))
        self.screen.update()
