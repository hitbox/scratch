from .pygame import pygame

def grid_template(rects, ncolumns):
    top = min(rect.top for rect in rects)
    left = min(rect.left for rect in rects)
    width = max(rect.width for rect in rects)
    height = max(rect.height for rect in rects)
    nrows = len(rects) // ncolumns
    #
    def make_rect(**position):
        rect = pygame.Rect(left, top, width, height)
        for key, value in position.items():
            setattr(rect, key, value)
        return rect

    cells = [make_rect()]
    for index in range(1, nrows * ncolumns):
        previous = cells[-1]
        if index % ncolumns == 0:
            position = dict(left=left, top=previous.bottom)
        else:
            position = dict(topleft=previous.topright)
        cell = make_rect(**position)
        cells.append(cell)
    return cells

def grid(rects, ncolumns):
    cells = grid_template(rects, ncolumns)
    for cell, rect in zip(cells, rects):
        rect.center = cell.center
