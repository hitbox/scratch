"""
--- Day 1: No Time for a Taxicab ---

Santa's sleigh uses a very high-precision clock to guide its movements, and the
clock's oscillator is regulated by stars. Unfortunately, the stars have been
stolen... by the Easter Bunny. To save Christmas, Santa needs you to retrieve
all fifty stars by December 25th.

Collect stars by solving puzzles. Two puzzles will be made available on each
day in the advent calendar; the second puzzle is unlocked when you complete the
first. Each puzzle grants one star. Good luck!

You're airdropped near Easter Bunny Headquarters in a city somewhere. "Near",
unfortunately, is as close as you can get - the instructions on the Easter
Bunny Recruiting Document the Elves intercepted start here, and nobody had time
to work them out further.

The Document indicates that you should start at the given coordinates (where
you just landed) and face North. Then, follow the provided sequence: either
turn left (L) or right (R) 90 degrees, then walk forward the given number of
blocks, ending at a new intersection.

There's no time to follow such ridiculous instructions on foot, though, so you
take a moment and work out the destination. Given that you can only walk on the
street grid of the city, how far is the shortest path to the destination?

For example:

Following R2, L3 leaves you 2 blocks East and 3 blocks North, or 5 blocks away.
R2, R2, R2 leaves you 2 blocks due South of your starting position, which is 2 blocks away.
R5, L5, R5, R3 leaves you 12 blocks away.
How many blocks away is Easter Bunny HQ?

--- Part Two ---

Then, you notice the instructions continue on the back of the Recruiting
Document. Easter Bunny HQ is actually at the first location you visit twice.

For example, if your instructions are R8, R4, R4, R8, the first location you
visit twice is 4 blocks away, due East.

How many blocks away is the first location you visit twice?
"""
import os

DIRECTIONS = NORTH, EAST, SOUTH, WEST = range(4)
MOVEMAP = { NORTH: (0, 1), WEST: (-1, 0), SOUTH: (0, -1), EAST: (1, 0) }

class Me(object):

    def __init__(self):
        self.position = (0, 0)
        self.direction = NORTH
        self.history = [self.position]

    def move(self, distance):
        mx, my = MOVEMAP[self.direction]
        for _ in range(distance):
            x, y = self.position
            self.position = (x + mx, y + my)
            self.history.append(self.position)

    def turn(self, direction):
        self.direction = (self.direction + direction) % len(DIRECTIONS)

    def navigate(self, instructions):
        for direction, distance in instructions:
            self.turn(direction)
            self.move(distance)
        return self.blocksto()

    def blocksto(self, position=None):
        if position is None:
            position = self.position
        return sum(map(abs, position))

    def first_twice(self):
        counter = {}
        for position in self.history:
            if position not in counter:
                counter[position] = 0
            counter[position] += 1
            if counter[position] == 2:
                return position


def instructions(text):
    m = { 'R': 1, 'L': -1 }
    rv = ( p.strip() for p in text.split(',') )
    rv = ( (m[p[0]], int(p[1:])) for p in rv )
    return rv

def tests():
    assert Me().navigate(instructions('R2, L3')) == 5
    assert Me().navigate(instructions('R2, R2, R2')) == 2
    assert Me().navigate(instructions('R5, L5, R5, R3')) == 12

    me = Me()
    me.navigate(instructions('R8, R4, R4, R8'))
    position = me.first_twice()
    assert me.blocksto(position) == 4

def load():
    return open(os.path.join(os.path.dirname(__file__), 'input.txt')).read()

def part1():
    print('Day 01, part 1: travelled %s blocks.' % Me().navigate(instructions(load())))

def part2():
    me = Me()
    me.navigate(instructions(load()))
    print('Day 01, part 2: %s blocks to first position visited twice.' % me.blocksto(me.first_twice()))

def main():
    tests()
    part1()
    part2()
