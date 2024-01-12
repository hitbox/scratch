import argparse
import unittest

class Test(unittest.TestCase):

    def test_squares(self):
        self.assertEqual(len(SQUARES), 9*9)

    def test_unitlist(self):
        self.assertEqual(len(UNITLIST), 9+9+9)

    def test_units(self):
        self.assertTrue(all(len(UNITS[s]) == 3 for s in SQUARES))

    def test_peers(self):
        # NOTES
        # 20 = 8 + 8 + (9 - 1 - 2 - 2)
        # - nine squares in a row minus the square itself
        # - nine squares in a column minus the square itself
        # - nine squares in a unit square, minus the square itself, minus the
        #   squares above and below; and on either side of the square.
        # The last number holds because it is already enforced by the first two
        # constraints?
        self.assertTrue(all(len(PEERS[s]) == 20 for s in SQUARES))

    def test_units_for_square(self):
        # - squares in same row
        # - squares in same column
        # - squares in unit square
        self.assertEqual(
            UNITS['C2'],
            [['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2'],
             ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'],
             ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']]
        )

    def test_peers_for_square(self):
        # - same as units minus the square itself and the four squares it is
        #   unnecessary to check
        self.assertEqual(
            PEERS['C2'],
            set(['A2', 'B2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2',
                 'C1', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
                 'A1', 'A3', 'B1', 'B3'])
        )


def cross(A, B):
    return [a+b for a in A for b in B]

DIGITS = '123456789'
ROWS = 'ABCDEFGHI'
COLS = DIGITS
SQUARES = cross(ROWS, COLS)

# all the groupings in lists of lists
UNITLIST = (
    # groups of rows
    [cross(ROWS, col) for col in COLS] +
    # groups of columns
    [cross(row, COLS) for row in ROWS] +
    # the nine 3x3 groups
    [cross(rs, cs)
     for rs in ('ABC', 'DEF', 'GHI')
     for cs in ('123', '456', '789')]
)

# square -> list of lists of units square exists in

def _unit(square):
    return (square, [unit for unit in UNITLIST if square in unit])

UNITS = dict(map(_unit, SQUARES))

# NOTES
# - units[square] -> list of lists of units the square exists in
# - sum([[...], [...], ..., [...]], []) -> flattens the list of lists by
#   setting start to a list so that the plus operator works

def _peers(square):
    return (square, set(sum(UNITS[square], [])) - set([square]))

PEERS = dict(map(_peers, SQUARES))

def eliminate(values, s, d):
    """
    Eliminate d from values[s]; propagate when values or places <= 2. Return
    values, except return False if a contradiction is detected.
    """
    if d not in values[s]:
        # Already eliminated
        return values
    values[s] = values[s].replace(d,'')
    # (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
    if len(values[s]) == 0:
        # Contradiction: removed last value
        return False
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in PEERS[s]):
            return False
    # (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in UNITS[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            # Contradiction: no place for this value
            return False
        elif len(dplaces) == 1:
            # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d):
                return False
    return values

def assign(values, s, d):
    """
    Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected.
    """
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '0' or '.' for empties.
    """
    chars = [c for c in grid if c in DIGITS or c in '0.']
    assert len(chars) == 81
    return dict(zip(SQUARES, chars))

def parse_grid(grid):
    """
    Convert grid to a dict of possible values, {square: digits}, or return
    False if a contradiction is detected.
    """
    # To start, every square can be any digit; then assign values from the grid.
    values = dict((square, DIGITS) for square in SQUARES)
    for square, d in grid_values(grid).items():
        if d in DIGITS and not assign(values, square, d):
            # Fail if we can't assign d to square s.
            return False
    return values

def solved(values):
    """
    A puzzle is solved if each unit is a permutation of the digits 1 to 9.
    """
    def unitsolved(unit):
        return set(values[s] for s in unit) == set(digits)
    return values is not False and all(unitsolved(unit) for unit in unitlist)

def search(values):
    """
    Using depth-first search and propagation, try all possible values.
    """
    if values is False:
        # Failed earlier
        return False
    if all(len(values[s]) == 1 for s in SQUARES):
        # Solved!
        return values
    # Chose the unfilled square s with the fewest possibilities
    n, s = min((len(values[s]), s) for s in SQUARES if len(values[s]) > 1)
    for d in values[s]:
        result = search(assign(values.copy(), s, d))
        if result:
            return result

def solve(grid):
    return search(parse_grid(grid))

def display(values):
    """
    Display these values as a 2-D grid.
    """
    width = 1 + max(len(values[s]) for s in SQUARES)
    line = '+'.join(['-'*(width*3)]*3)
    for row in ROWS:
        print(''.join(values[row+col].center(width) + ('|' if col in '36' else '')
                      for col in COLS))
        if row in 'CF':
            print(line)
    print()

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('grid')
    args = parser.parse_args(argv)

    solution = solve(args.grid)
    display(solution)

if __name__ == '__main__':
    main()
