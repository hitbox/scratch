import re
import pdb
import os
from pprint import pprint as pp

def printable(screen):
    return '\n'.join(''.join(row) for row in screen)

def rotate(sequence, amount):
    return sequence[amount:] + sequence[:amount]

class Screen(object):

    def __init__(self, rows=6, columns=50):
        self._screen = [ ['.' for col in range(columns)] for row in range(rows) ]

    def __str__(self):
        return printable(self._screen)

    def pixels(self):
        for row in self._screen:
            yield from row

    def execute(self, instructions):
        rect_re = re.compile('^rect (\d+)x(\d+)$')
        rotate_re = re.compile('^rotate (row|column) [xy]=(\d+) by (\d+)$')

        for instruction in instructions:
            match = rect_re.match(instruction)
            if match:
                width, height = map(int, match.groups())
                self.rect(width, height)

            match = rotate_re.match(instruction)
            if match:
                type_, position, pixels = match.groups()
                position = int(position)
                pixels = int(pixels)
                func = getattr(self, 'rotate_' + type_)
                func(position, pixels)

    def rect(self, width, height):
        for r in range(height):
            for c in range(width):
                self._screen[r][c] = '#'

    def rotate_row(self, row, pixels):
        rv = rotate(self._screen[row], -pixels)
        self._screen[row] = rv

    def rotate_column(self, column, pixels):
        tmp = list(map(list, zip(*self._screen)))
        tmp[column] = rotate(tmp[column], -pixels)
        rv = list(map(list, zip(*tmp)))
        self._screen = rv


def load():
    return open(os.path.join(os.path.dirname(__file__), 'input.txt')).readlines()

def tests():
    screen = Screen(3, 7)
    screen.rect(3, 2)
    assert str(screen) == '###....\n###....\n.......'

    screen.rotate_column(1, 1)
    assert str(screen) == '#.#....\n###....\n.#.....'

    screen.rotate_row(0, 4)
    assert str(screen) == '....#.#\n###....\n.#.....'

    screen.rotate_column(1, 1)
    assert str(screen) == '.#..#.#\n#.#....\n.#.....'

def part1():
    screen = Screen()
    screen.execute(load())
    print('Day 8, part 1: Number of lit pixels %s' % sum(1 for p in screen.pixels() if p == '#'))

def part2():
    screen = Screen()
    screen.execute(load())
    print('Day 8, part 2: Code displayed below')
    print(screen)

def main():
    tests()
    part1()
    part2()
