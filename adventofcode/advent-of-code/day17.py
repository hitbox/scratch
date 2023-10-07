#!python
import os
from itertools import permutations, combinations
from pprint import pprint as pp
from adventlib import input_path

class Container(object):

    def __init__(self, n):
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return '<Container(%s)>' % self.n


def find_combos(store, containers):
    combos = set(tuple(sorted(p, key=lambda p: p.n))
                       for r in range(1, len(containers) + 1)
                       for p in combinations(containers, r))

    solutions = [ c for c in combos if sum(i.n for i in c) == store ]
    return solutions

def test():
    store = 25

    twenty = Container(20)
    fifteen = Container(15)
    ten = Container(10)
    five_first = Container(5)
    five_second = Container(5)

    containers = (twenty, fifteen, ten, five_first, five_second)

    solutions = find_combos(store, containers)
    solutions_sets = [set(c) for c in solutions]

    assert set([fifteen, ten]) in solutions_sets
    assert set([twenty, five_first]) in solutions_sets
    assert set([twenty, five_second]) in solutions_sets
    assert set([fifteen, five_first, five_second]) in solutions_sets

def main():
    store = 150

    with open(input_path(__file__, 1)) as f:
        containers = tuple(Container(int(line)) for line in f.readlines())

    solutions = find_combos(store, containers)
    print 'Part 1: %s' % (len(solutions), )
    
    min_containers = min(len(solution) for solution in solutions)
    num_min_cans = len([solution for solution in solutions if len(solution) == min_containers])
    print 'Part 2: %s' % (num_min_cans, )


if __name__ == '__main__':
    test()
    main()
