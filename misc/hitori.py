import argparse
import unittest

from collections import Counter

neighbor_deltas = set(tuple(x - 1 for x in divmod(i, 3)) for i in range(9))
neighbor_deltas.remove((0,0))

side_deltas = set((dy, dx) for dy, dx in neighbor_deltas if abs(dy) != abs(dx))

rules = [
    'Color cells so no number appears more than once in a row or column.',
    'The sides of colored cells never touch.',
    'Uncolored cells form a continuous network.',
]

sample = [
    [1,1,2,4,3,5],
    [1,1,5,4,4,6],
    [4,6,6,2,1,1],
    [6,3,3,3,5,4],
    [2,3,4,1,6,5],
    [2,5,4,6,2,5],
]

class TestHitori(unittest.TestCase):

    no_island_states = [
        [
            [0,    0,    0],
            [None, 0,    None],
            [0,    None, 0],
        ],
        [
            [0,    None, 0],
            [None, 0,    0],
            [0,    None, 0],
        ],
        [
            [0,    None, 0],
            [None, 0,    None],
            [0,    0,    0],
        ],
        [
            [0,    None, 0],
            [0,    0,    None],
            [0,    None, 0],
        ],
    ]

    has_island_states = [
        [
            [0,    None, 0],
            [None, 0,    None],
            [0,    None, 0],
        ],
    ]

    solved_state = [
        [None, 1,    2,    4,    3, None],
        [1,    None, 5,    None, 4, 6   ],
        [4,    6,    None, 2,    1, None],
        [6,    None, 3,    None, 5, 4   ],
        [2,    3,    4,    1,    6, 5   ],
        [None, 5,    None, 6,    2, None],
    ]

    def test_is_island(self):
        # all side neighbors are None
        for state in self.has_island_states:
            self.assertTrue(is_island((1,1), state))

    def test_is_not_island(self):
        # top, right, bottom, left
        for not_island in self.no_island_states:
            self.assertFalse(is_island((1,1), not_island))

    def test_has_no_island(self):
        self.assertFalse(has_island(self.solved_state))

    def test_is_square(self):
        for state in self.no_island_states + [self.solved_state]:
            self.assertTrue(is_square(state))

    def test_is_solved(self):
        self.assertTrue(is_solved(self.solved_state))

    def test_iterate_duplicates(self):
        # empty, no dupes
        result = list(iterate_duplicates([]))
        self.assertEqual(result, [])
        # no dupes
        result = list(iterate_duplicates(range(5)))
        self.assertEqual(result, [])
        # one duplicate, at positions one and two
        result = list(iterate_duplicates([1,2,2,3]))
        self.assertEqual(result, [(1, 2), (2, 2)])


def iterate(state):
    for row_index, row in enumerate(state):
        for col_index, value in enumerate(row):
            yield ((row_index, col_index), value)

def iterate_deltas(origin, state, deltas):
    y, x = origin
    nrows = len(state)
    ncols = len(list(zip(*state)))
    for dy, dx in deltas:
        npos = (ny, nx) = (y + dy, x + dx)
        if -1 < ny < nrows and -1 < nx < ncols:
            nvalue = state[ny][nx]
            yield (npos, nvalue)

def iterate_neighbors(origin, state):
    yield from iterate_deltas(origin, state, neighbor_deltas)

def iterate_sides(origin, state):
    yield from iterate_deltas(origin, state, side_deltas)

def cells_at_row(state, row):
    for cell in state[row]:
        yield cell

def cells_at_col(state, col):
    for row in state:
        yield row[col]

def is_square(state):
    nrows = len(state)
    ncols = len(list(zip(*state, strict=True)))
    return nrows == ncols

def is_island(position, state):
    """
    The cell at `postition` is surrounded by None, on its sides.
    """
    return all(value is None for _, value in iterate_sides(position, state))

def has_island(state):
    """
    The grid contains an island cell.
    """
    return any(is_island(position, state) for position, _ in iterate(state))

def is_solved(state):
    for dimension in (state, zip(*state)):
        for values in dimension:
            # ignore the None items, only the numbers must be unique
            numbers = [val for val in values if isinstance(val, int)]
            if len(set(numbers)) != len(numbers):
                return False
    return not has_island(state)

def duplicates(values):
    return {val for val, count in Counter(values).items() if count > 1}

def iterate_duplicates(values):
    counts = Counter(values)
    for index, value in enumerate(values):
        if counts[value] > 1:
            yield (index, value)

def copy(state, remove_position):
    newstate = []
    for row_index, row in enumerate(state):
        newrow = []
        newstate.append(newrow)
        for col_index, value in enumerate(row):
            if (row_index, col_index) == remove_position:
                newrow.append(None)
            else:
                newrow.append(value)
    return newstate

def hitori(state):
    if is_solved(state):
        return state
    for row_index, row in enumerate(state):
        for col_index, _ in iterate_duplicates(row):
            print(copy(state, (row_index, col_index)))
            return

def run():
    hitori(sample)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()

# 2023-11-30
# - https://rdivyanshu.github.io/haunted.html
# - https://rdivyanshu.github.io/asp.html
# - https://www.nikoli.co.jp/en/puzzles/hitori/
# - Made it to making tests for the neighbors iterators.
