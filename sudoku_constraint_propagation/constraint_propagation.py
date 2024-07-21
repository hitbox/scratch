"""
Constraint propagation is a powerful technique often used in constraint
satisfaction problems (CSPs) to reduce the search space by iteratively
narrowing the possible values for the variables involved. A common example of
constraint propagation is in solving Sudoku puzzles.

Here's a step-by-step explanation and implementation of constraint propagation
using the AC-3 algorithm (Arc-Consistency 3) for a Sudoku puzzle:

Explanation

    Variables:
        Each cell in the Sudoku grid is a variable.
    Domains:
        The domain of each variable (cell) is the set of possible values it can
        take (initially, 1-9).
    Constraints:
        Each row, column, and 3x3 subgrid must contain all digits from 1 to 9
        without repetition.

The AC-3 algorithm works by maintaining a queue of arcs (pairs of variables)
and iteratively making each pair arc-consistent. An arc (X, Y) is
arc-consistent if, for every value in the domain of X, there is some value in
the domain of Y that satisfies the constraint between X and Y.

Implementation

Here's the implementation of constraint propagation using the AC-3 algorithm
for solving Sudoku:
"""
import argparse

from pprint import pprint

class CSP:

    def __init__(self, variables, domains, neighbors, constraints):
        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints


def print_domains(domains):
    pprint(domains.items())

def print_sudoku(puzzle):
    for row in puzzle:
        print(''.join('_' if d == 0 else str(d) for d in row))

def constraints_domains(csp, xi, xj, x):
    for y in csp.constraints[(xi, xj)](x):
        yield (y in csp.domains[xj])

def revise(csp, xi, xj):
    revised = False
    for x in csp.domains[xi]:
        #if not any(y in csp.domains[xj] for y in csp.constraints[xi, xj](x)):
        if not any(constraints_domains(csp, xi, xj, x)):
            csp.domains[xi].remove(x)
            revised = True
    return revised

def ac3(csp):
    queue = [(xi, xj) for xi in csp.variables for xj in csp.neighbors[xi]]
    while queue:
        (xi, xj) = queue.pop(0)
        if revise(csp, xi, xj):
            if not csp.domains[xi]:
                return False
            for xk in csp.neighbors[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True

def sudoku_domain(initial_value):
    if initial_value == 0:
        return list(range(1, 10))
    else:
        return [initial_value]

def sudoku_csp(puzzle):
    variables = [(r, c) for r in range(9) for c in range(9)]
    domains = {
        (r, c): sudoku_domain(puzzle[r][c]) for r in range(9) for c in range(9)
    }
    neighbors = {
        (r, c):
            [(r, j) for j in range(9) if j != c]
            + [(i, c) for i in range(9) if i != r]
            + [
                cell
                for i in range(3)
                for j in range(3)
                if (cell := (r//3*3 + i, c//3*3 + j)) != (r, c)
            ]
            for r in range(9)
            for c in range(9)
    }
    constraints = {
        (var1, var2):
            lambda x: [x] for var1 in variables for var2 in neighbors[var1]
    }
    return CSP(variables, domains, neighbors, constraints)

def parse_sudoku_line(line):
    numbers = list(map(int, line))
    puzzle = [numbers[i:i+9] for i in range(0, 9*9, 9)]
    assert len(puzzle) == 9
    for row in puzzle:
        assert len(row) == 9
    return puzzle

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--sudoku')
    args = parser.parse_args(argv)

    # chatgpt's code doesn't solve its own puzzle or sudoku1.txt
    puzzle = parse_sudoku_line(args.sudoku)
    csp = sudoku_csp(puzzle)
    pprint(csp.neighbors[(0,0)])
    return
    print(ac3(csp))

if __name__ == '__main__':
    main()

"""
Breakdown

    ac3 Function:
        This function maintains a queue of arcs and makes each arc consistent.
        If any domain becomes empty, it returns False, indicating that the
        problem is unsolvable.
    Revise Function:
        This function revises the domain of xi by removing values that do not
        satisfy the constraint with xj.
    CSP Class:
        Represents a constraint satisfaction problem with variables, domains,
        neighbors, and constraints.
    sudoku_csp Function:
        Initializes the CSP for the Sudoku puzzle, setting up variables,
        domains, neighbors, and constraints.

This code sets up the Sudoku puzzle, applies the AC-3 algorithm for constraint
propagation, and prints the solved puzzle if a solution is found.
"""
