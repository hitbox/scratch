from itertools import product

N = 9*9
grid = [[0 for _ in range(N)] for _ in range(N)]

for row in grid:
    for value in row:
        pass

for col in zip(*grid):
    for value in col:
        pass

for y, x in product(range(0,9,3), repeat=2):
    # this way doesn't tell us what square we're in but the calculation would be trivial
    values = [grid[y+i][x+j] for i, j in product(range(3), repeat=2)]
