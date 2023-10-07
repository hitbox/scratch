from framework import align
from framework import style
from framework.pygame import pygame

class SudokuBoard:

    def make_rects(self, board):
        size = style.get('sudoku.cell', 'size')
        rects = [pygame.Rect((0,0),size) for row in board for col in row]
        align.grid_template(rects, 9)
        return rects
