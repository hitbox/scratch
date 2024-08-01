import argparse

from pprint import pprint

def parse_sudoku_line(line):
    numbers = list(map(int, line.strip()))
    rows = [numbers[i:i+9] for i in range(0, 9*9, 9)]
    assert len(rows) == 9
    for row in rows:
        assert len(row) == 9
    return rows

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('puzzle')
    args = parser.parse_args(argv)

    puzzle = parse_sudoku_line(args.puzzle)

    variables = [(r, c) for r in range(9) for c in range(9)]

    domains = {(r, c): set(range(1,10)) for r in range(9) for c in range(9)}

    neighbors = {}
    for r in range(9):
        for c in range(9):
            neighbors[(r, c)] = set()
            # row neighbors
            for j in range(9):
                if j != c:
                    neighbors[(r, c)].add((r, j))
            # column neighbors
            for i in range(9):
                if i != r:
                    neighbors[(r, c)].add((i, c))
            # latin square neighbors
            for j in range(3):
                for i in range(3):
                    cell = (r // 3 * 3 + j, c // 3 * 3 + i)
                    if (r, c) != cell:
                        neighbors[(r, c)].add(cell)

    # insert puzzle and update cell possibilities
    cells = [(r, c) for r in range(9) for c in range(9)]
    while cells:
        r, c = cells.pop()
        digit = puzzle[r][c]
        if digit == 0:
            continue
        domain = domains[(r, c)]
        domain.clear()
        domain.add(digit)
        for cell in neighbors[(r, c)]:
            domains[cell].discard(digit)

    # print remaining possibilities
    for r in range(9):
        cols = []
        for c in range(9):
            domain = domains[(r, c)]
            digits = ''.join(map(str, sorted(domain)))
            cols.append(f'{digits:^9}')
        if r > 0 and r % 3 == 0:
            print()
        print(' '.join(cols))

if __name__ == '__main__':
    main()
