from framework import style

def init():
    style.set('framework.render.box', 'background.color', (200,10,10))
    style.set('framework.render.box', 'border.color', (200,)*3)
    #
    style.set('sudoku.cell', 'size', (16,)*2)
    #style.set('sudoku.cell', 'background.color', (10,10,200))
    style.set('sudoku.cell', 'border.color', (200,)*3)
    style.set('sudoku.cell', 'border.width', 1)
    style.set('sudoku.cell', 'font', 'pygame.font.Font(None, 24)')
