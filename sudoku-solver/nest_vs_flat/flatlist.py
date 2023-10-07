from itertools import product

N = 9*9
flat = [0 for _ in range(N)]

for index, value in enumerate(flat):
    row, col = divmod(index, 9)
    sqrow = (row % 3)
    sqcol = (col // 3)
    #
    column_values = [flat[ci] for ci in range(col, N, 9)]
    row_values = [flat[ri] for ri in range(row*9, row*9+9)]
    square_values = [
        flat[ (sqrow*3+rowoff) * 9 + (sqcol*3+coloff) ]
        for rowoff, coloff in product(range(3), repeat=2)
    ]
