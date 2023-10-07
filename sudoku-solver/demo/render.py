from framework import align
from framework import render
from framework import style
from framework import wrap
from framework.pygame import pygame

from .board import SudokuBoard

def render_sudoku(board):
    size = style.get('sudoku.cell', 'size', (4,)*2)
    rects = [pygame.Rect((0,0), size) for row in board for _ in row]
    align.grid(rects, 9)
    rect = wrap.rects(rects)
    cell_image = render.box('sudoku.cell')
    surface = pygame.Surface(rect.size, flags=pygame.SRCALPHA)
    for rect in rects:
        surface.blit(cell_image, rect)
    return surface

class BoardRenderer:

    def __init__(self):
        self.font = style.get('sudoku.cell', 'font')
        if isinstance(self.font, str):
            pygame.font.init()
            self.font = eval(self.font)
        self.guiboard = SudokuBoard()

    def render(self, board):
        rects = self.guiboard.make_rects(board)
        align.grid(rects, 9)
        whole = wrap.rects(rects)
        image = pygame.Surface(whole.size)
        cell_image = render.box('sudoku.cell')
        for rect in rects:
            image.blit(cell_image, rect)
        return image
