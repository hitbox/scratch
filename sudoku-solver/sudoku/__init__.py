from itertools import product

NUMBERS = set(range(1,10))

def cellinfo(index):
    """
    Return what (row,col), topleft cell of square, and square; this index would
    be in.
    """
    row, col = divmod(index, 9)
    sqrow = row // 3
    sqcol = col // 3
    square = sqrow * 3 + sqcol
    return ((row,col), (sqrow,sqcol), square)

def is_solved(board):
    """
    Return Sudoku board is solved.
    """
    for row in board:
        if set(row).isdisjoint(NUMBERS):
            return False

    columns = zip(*board)
    for column in columns:
        if set(column).isdisjoint(NUMBERS):
            return False

    for x, y in product(range(0,9,3),repeat=2):
        square = [board[y+i][x+j] for i, j in product(range(3),repeat=2)]
        if set(square).isdisjoint(NUMBERS):
            return False

    return True

def new_board():
    board = [ [0 for _ in range(9)] for _ in range(9) ]
    return board

def possible_numbers(board, index):
    """
    Available numbers for cell in Sudoku board.
    """
    (row,col), (sqrow,sqcol), square = cellinfo(index)
    row_values = set(board[row])
    col_values = list(zip(*board))[col]
    sqr_values = [board[sqrow+offx][sqcol+offy] for offx, offy in product(range(3), repeat=2)]
    existing = set(row_values).union(col_values).union(sqr_values)
    return NUMBERS.difference(existing)
