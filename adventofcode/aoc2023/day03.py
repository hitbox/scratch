import argparse
import unittest

from collections import defaultdict
from itertools import combinations

part1_text = """
--- Day 3: Gear Ratios ---

You and the Elf eventually reach a gondola lift station; he says the gondola
lift will take you up to the water source, but this is as far as he can bring
you. You go inside.

It doesn't take long to find the gondolas, but there seems to be a problem:
they're not moving.

"Aaah!"

You turn around to see a slightly-greasy Elf with a wrench and a look of
surprise. "Sorry, I wasn't expecting anyone! The gondola lift isn't working
right now; it'll still be a while before I can fix it." You offer to help.

The engineer explains that an engine part seems to be missing from the engine,
but nobody can figure out which one. If you can add up all the part numbers in
the engine schematic, it should be easy to work out which part is missing.

The engine schematic (your puzzle input) consists of a visual representation of
the engine. There are lots of numbers and symbols you don't really understand,
but apparently any number adjacent to a symbol, even diagonally, is a "part
number" and should be included in your sum. (Periods (.) do not count as a
symbol.)

Here is an example engine schematic:

467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598..

In this schematic, two numbers are not part numbers because they are not
adjacent to a symbol: 114 (top right) and 58 (middle right). Every other number
is adjacent to a symbol and so is a part number; their sum is 4361.

Of course, the actual engine schematic is much larger. What is the sum of all
of the part numbers in the engine schematic?
"""

part2_text = """
--- Part Two ---

The engineer finds the missing part and installs it in the engine! As the
engine springs to life, you jump in the closest gondola, finally ready to
ascend to the water source.

You don't seem to be going very fast, though. Maybe something is still wrong?
Fortunately, the gondola has a phone labeled "help", so you pick it up and the
engineer answers.

Before you can explain the situation, she suggests that you look out the
window. There stands the engineer, holding a phone in one hand and waving with
the other. You're going so slowly that you haven't even left the station. You
exit the gondola.

The missing part wasn't the only issue - one of the gears in the engine is
wrong. A gear is any * symbol that is adjacent to exactly two part numbers. Its
gear ratio is the result of multiplying those two numbers together.

This time, you need to find the gear ratio of every gear and add them all up so
that the engineer can figure out which gear needs to be replaced.

Consider the same engine schematic again:

467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598..

In this schematic, there are two gears. The first is in the top left; it has
part numbers 467 and 35, so its gear ratio is 16345. The second gear is in the
lower right; its gear ratio is 451490. (The * adjacent to 617 is not a gear
because it is only adjacent to one part number.) Adding up all of the gear
ratios produces 467835.

What is the sum of all of the gear ratios in your engine schematic?
"""

class Tests(unittest.TestCase):

    example_lines = [
        '467..114..',
        '...*......',
        '..35..633.',
        '......#...',
        '617*......',
        '.....+.58.',
        '..592.....',
        '......755.',
        '...$.*....',
        '.664.598..',
    ]

    def test_parse(self):
        expect = {
            (0,0): 4, (0,1): 6, (0,2): 7, # 467
            (0,5): 1, (0,6): 1, (0,7): 4, # 114
            (1,3): '*',
            (2,2): 3, (2,3): 5, # 35
            (2,6): 6, (2,7): 3, (2,8): 3, # 633
            (3,6): '#',
            (4,0): 6, (4,1): 1, (4,2): 7, # 617
            (4,3): '*',
            (5,5): '+',
            (5,7): 5, (5,8): 8, # 58
            (6,2): 5, (6,3): 9, (6,4): 2, # 592
            (7,6): 7, (7,7): 5, (7,8): 5, # 755
            (8,3): '$', (8,5): '*',
            (9,1): 6, (9,2): 6, (9,3): 4, # 664
            (9,5): 5, (9,6): 9, (9,7): 8, # 598
        }
        self.assertEqual(parse(self.example_lines), expect)

    def test_find_digits(self):
        schematic = parse(self.example_lines)
        expect = ((0,0), [4,6,7])
        self.assertEqual(expect, find_digits(schematic, (0,0)))
        self.assertEqual(expect, find_digits(schematic, (0,1)))
        self.assertEqual(expect, find_digits(schematic, (0,2)))
        expect = ((6,2), [5,9,2])
        self.assertEqual(expect, find_digits(schematic, (6,2)))
        self.assertEqual(expect, find_digits(schematic, (6,3)))
        self.assertEqual(expect, find_digits(schematic, (6,4)))

    def test_solve(self):
        schematic = parse(self.example_lines)
        self.assertEqual(solve(schematic), 4361)

    def test_iterint(self):
        self.assertEqual(iterint([]), 0)
        self.assertEqual(iterint([1]), 1)
        self.assertEqual(iterint([1,1,1]), 111)
        self.assertEqual(iterint([1,0,0,0]), 1000)
        self.assertEqual(iterint([1,0,1,0]), 1010)

    def test_from_reddit(self):
        # fixed mistake of testing integers' truth value
        # should have tested for is None
        lines = [
            '12.......*..',
            '+.........34',
            '.......-12..',
            '..78........',
            '..*....60...',
            '78..........',
            '.......23...',
            '....90*12...',
            '............',
            '2.2......12.',
            '.*.........*',
            '1.1.......56',
        ]
        schematic = parse(lines)
        self.assertTrue(any(x == 0 for x in schematic.values()))
        self.assertEqual(solve(schematic), 413)

    def test_find_gear_ratios(self):
        schematic = parse(self.example_lines)
        self.assertEqual(solve_gear_ratios(schematic), 467835)


neighbor_deltas = set(tuple(x - 1 for x in divmod(i, 3)) for i in range(9))
neighbor_deltas.remove((0,0))

def iter_neighbors(schematic, origin):
    y, x = origin
    for dy, dx in neighbor_deltas:
        other_pos = (y + dy, x + dx)
        if other_pos in schematic:
            yield (other_pos, schematic[other_pos])

def find_digits(schematic, position):
    """
    Given a position of a digit in the schematic, find all the digits and their
    origin position.
    """
    assert position in schematic and isinstance(schematic[position], int)
    y, x = position
    while (y, x-1) in schematic and isinstance(schematic[(y, x-1)], int):
        x -= 1
    origin = (y, x)
    digits = [
        schematic[origin]
    ]
    while (y,x+1) in schematic and isinstance(schematic[(y, x+1)], int):
        x += 1
        digits.append(schematic[(y, x)])
    return (origin, digits)

def is_symbol(value):
    return isinstance(value, str)

def iter_part_digits(schematic, isfunc=is_symbol):
    for pos, val in schematic.items():
        if not isfunc(val):
            continue
        # (pos, val) is symbol
        for other_pos, other_value in iter_neighbors(schematic, pos):
            if not isinstance(other_value, int):
                continue
            # neighboring digit is part of number
            yield find_digits(schematic, other_pos)

def get_part_digits(schematic):
    part_digits = {}
    for origin, digits in iter_part_digits(schematic):
        if origin not in part_digits:
            part_digits[origin] = digits
    return part_digits

def iterint(digits):
    return sum(d*10**i for i, d in enumerate(reversed(digits)))

def solve(schematic):
    part_digits = get_part_digits(schematic)
    part_numbers = map(iterint, part_digits.values())
    return sum(part_numbers)

def solve_gear_ratios(schematic):
    answer = 0
    for gear_pos, gear_val in schematic.items():
        if gear_val != '*':
            continue
        adjacent = {}
        for other_pos, other_value in iter_neighbors(schematic, gear_pos):
            if not isinstance(other_value, int):
                continue
            # neighboring digit is part of number
            other_origin, other_digits = find_digits(schematic, other_pos)
            if other_origin not in adjacent:
                adjacent[other_origin] = other_digits
        if len(adjacent) != 2:
            continue
        pn1, pn2 = map(iterint, adjacent.values())
        answer += pn1 * pn2
    return answer

def parse_char(char):
    assert isinstance(char, str) and len(char) == 1
    if char.isdigit():
        return int(char)
    elif char != '.':
        return char

def parse_line(line):
    for col_index, char in enumerate(line):
        yield (col_index, parse_char(char))

def parse_lines(lines):
    for row_index, line in enumerate(lines):
        for col_index, value in parse_line(line):
            if value is not None:
                yield ((row_index, col_index), value)

def parse(lines):
    return {pos: value for pos, value in parse_lines(lines)}

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input',
        default = 'inputs/day03.txt',
        type = argparse.FileType(),
    )
    args = parser.parse_args(argv)

    schematic = parse(map(str.strip, args.input))
    part1_answer = solve(schematic)
    assert part1_answer == 527144
    print(f'{part1_answer=}')

    part2_answer = solve_gear_ratios(schematic)
    print(f'{part2_answer=}')
    # 81463996

if __name__ == '__main__':
    main()
