import argparse
import os

from itertools import combinations
from pprint import pprint as pp

class Direction(int):

    def __new__(cls, *args, **kwargs):
        value, name = args[:2]
        inst = super(Direction, cls).__new__(cls, value)
        inst.name = name
        return inst

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        return self.value + other


DIRS = UP, DOWN = Direction(1, 'UP'), Direction(-1, 'DOWN')

from .facility import Facility
from . import astar, tests
from .utils import *

def part1():
    start = Facility(load())
    goal = make_goal(start)

    print(start)
    print()
    print(goal)
    print()

    came_from, cost = astar.find(start, goal)
    astar.draw(came_from, start, goal)

# 1. elevator capacity two microchips or generators
# 2. elevator must have at least one microchip or generator to move
# 3. chip must be connected to its generator to exist on the same floor as a
# different generator

def main():
    tests.run()
    part1()
