import os
import re
import heapq
import math
from collections import namedtuple
from itertools import combinations, chain

empty = frozenset()

FLOORS = {0, 1, 2, 3}

class Floor(frozenset):

    def __str__(self):
        return ','.join(self)


_State = namedtuple('_State', 'elevator floors')

class State(_State):

    def __new__(cls, elevator, floors):
        self = super(State, cls).__new__(cls, elevator, tuple(map(frozenset, floors)))
        self.__slots__ = ('elevator', 'floors')
        return self

    def __str__(self):
        return self.prettyprint()

    def prettyprint(self):
        floorfmt = 'F{} {:1} {}\n'.format
        space = ' '.join
        s = ''
        for floor_number in sorted(FLOORS, reverse=True):
            s += floorfmt(floor_number + 1,
                          'E' if self.elevator == floor_number else '',
                          space(map(str, sorted(self.floors[floor_number]))))
        return s


thingtype = lambda thing: thing[0]

isgen = lambda thing: thing.endswith('G')
ischip = lambda thing: thing.endswith('M')

def legal(state):
    for floor in state.floors:
        if not floor:
            continue

        gens = tuple(map(thingtype, filter(isgen, floor)))
        chips = tuple(map(thingtype, filter(ischip, floor)))

        if not (gens and chips):
            continue

        loosegens = tuple(gen for gen in gens if gen not in chips)
        loosechips = tuple(chip for chip in chips if chip not in gens)

        if loosegens and loosechips:
            return False

    return True


def combos(things):
    for s in chain(combinations(things, 1), combinations(things, 2)):
        yield frozenset(s)

def moves(state):
    E, floors = state
    for E2 in {E + 1, E - 1} & FLOORS:
        for stuff in combos(state.floors[E]):
            newfloors = tuple(
                    s | stuff if i == E2 else
                    s - stuff if i == E else
                    s
                    for i,s in enumerate(state.floors))
            neighbor = State(E2, newfloors)
            if legal(neighbor):
                yield neighbor

def heuristic(state):
    total = sum(len(floor) * i for i, floor in enumerate(reversed(state.floors)))
    return math.ceil(total / 2)

def path(previous, goal):
    return [] if goal is None else path(previous, previous[goal]) + [goal]

def astar(start):
    frontier = [(heuristic(start), start)]

    previous = {start: None}
    costs = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        x = heuristic(current)
        if x == 0:
            return path(previous, current)

        for neighbor in moves(current):
            cost = costs[current] + 1
            if neighbor not in costs or cost < costs[neighbor]:
                heapq.heappush(frontier, (cost + heuristic(neighbor), neighbor))
                costs[neighbor] = cost
                previous[neighbor] = current

def load():
    return open(os.path.join(os.path.dirname(__file__), 'input.txt')).read()

def parse(text):
    getthings = re.compile('AN? (\w+)(?:-COMPATIBLE)? (GENERATOR|MICROCHIP)').findall

    abbrev2name = {}
    name2abbrev = {}

    def abbrevthings(things):
        for name, type_ in things:
            type_ = type_[0]
            if name not in name2abbrev:
                for char in name:
                    if char not in abbrev2name:
                        abbrev2name[char] = name
                        name2abbrev[name] = char
                        break
            yield name2abbrev[name] + type_

    for line in text.upper().splitlines():
        things = getthings(line)
        yield Floor(abbrevthings(things))

def tests():
    assert not legal(State(0, ({'RG', 'LM'}, empty, empty, empty)))

    start = State(0, ({'RG'}, empty, {'RM'}, empty))
    assert legal(start)

    pathlist = astar(start)
    for state in pathlist:
        print(state)

    start = State(0, ({'HM', 'LM'}, {'HG'}, {'LG'}, empty))
    print(start)
    pathlist = astar(start)
    for state in pathlist:
        print(state)
    print(len(pathlist))

def part1():
    start = State(0, parse(load()))
    print(start)

    pathlist = astar(start)
    for state in pathlist:
        print(state)

    print(len(pathlist) - 1)

def part2():
    text = """The first floor contains a polonium generator, a thulium generator, a thulium-compatible microchip, a promethium generator, a ruthenium generator, a ruthenium-compatible microchip, a cobalt generator, and a cobalt-compatible microchip. An elerium generator. An elerium-compatible microchip. A dilithium generator. A dilithium-compatible microchip.
The second floor contains a polonium-compatible microchip and a promethium-compatible microchip.
The third floor contains nothing relevant.
The fourth floor contains nothing relevant."""

    start = State(0, tuple(parse(text)))
    print(start)
    pathlist = astar(start)
    for state in pathlist:
        print(state)

    print(len(pathlist) - 1)

def main():
    #tests()
    #part1()
    part2()
