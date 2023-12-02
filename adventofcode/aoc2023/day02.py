import argparse
import re
import unittest

from collections import defaultdict
from functools import reduce
from itertools import repeat
from operator import mul

# https://adventofcode.com/2023/day/2

part1_text = """
--- Day 2: Cube Conundrum ---

You're launched high into the atmosphere! The apex of your trajectory just
barely reaches the surface of a large island floating in the sky. You gently
land in a fluffy pile of leaves. It's quite cold, but you don't see much snow.
An Elf runs over to greet you.

The Elf explains that you've arrived at Snow Island and apologizes for the lack
of snow. He'll be happy to explain the situation, but it's a bit of a walk, so
you have some time. They don't get many visitors up here; would you like to
play a game in the meantime?

As you walk, the Elf shows you a small bag and some cubes which are either red,
green, or blue. Each time you play this game, he will hide a secret number of
cubes of each color in the bag, and your goal is to figure out information
about the number of cubes.

To get information, once a bag has been loaded with cubes, the Elf will reach
into the bag, grab a handful of random cubes, show them to you, and then put
them back in the bag. He'll do this a few times per game.

You play several games and record the information from each game (your puzzle
input). Each game is listed with its ID number (like the 11 in Game 11: ...)
followed by a semicolon-separated list of subsets of cubes that were revealed
from the bag (like 3 red, 5 green, 4 blue).

For example, the record of a few games might look like this:

Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green

In game 1, three sets of cubes are revealed from the bag (and then put back
again). The first set is 3 blue cubes and 4 red cubes; the second set is 1 red
cube, 2 green cubes, and 6 blue cubes; the third set is only 2 green cubes.

The Elf would first like to know which games would have been possible if the
bag contained only 12 red cubes, 13 green cubes, and 14 blue cubes?

In the example above, games 1, 2, and 5 would have been possible if the bag had
been loaded with that configuration. However, game 3 would have been impossible
because at one point the Elf showed you 20 red cubes at once; similarly, game 4
would also have been impossible because the Elf showed you 15 blue cubes at
once. If you add up the IDs of the games that would have been possible, you get
8.

Determine which games would have been possible if the bag had been loaded with
only 12 red cubes, 13 green cubes, and 14 blue cubes. What is the sum of the
IDs of those games?
"""

part2_text = """
--- Part Two ---

The Elf says they've stopped producing snow because they aren't getting any
water! He isn't sure why the water stopped; however, he can show you how to get
to the water source to check it out for yourself. It's just up ahead!

As you continue your walk, the Elf poses a second question: in each game you
played, what is the fewest number of cubes of each color that could have been
in the bag to make the game possible?

Again consider the example games from earlier:

Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green

    In game 1, the game could have been played with as few as 4 red, 2 green,
    and 6 blue cubes. If any color had even one fewer cube, the game would have
    been impossible.
    Game 2 could have been played with a minimum of 1 red, 3 green, and 4 blue
    cubes.
    Game 3 must have been played with at least 20 red, 13 green, and 6 blue
    cubes.
    Game 4 required at least 14 red, 3 green, and 15 blue cubes.
    Game 5 needed no fewer than 6 red, 3 green, and 2 blue cubes in the bag.

The power of a set of cubes is equal to the numbers of red, green, and blue
cubes multiplied together. The power of the minimum set of cubes in game 1 is
48. In games 2-5 it was 12, 1560, 630, and 36, respectively. Adding up these
five powers produces the sum 2286.

For each game, find the minimum set of cubes that must have been present. What
is the sum of the power of these sets?
"""

class Tests(unittest.TestCase):

    lines = [
        'Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green',
        'Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue',
        'Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red',
        'Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red',
        'Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green',
    ]

    def test_parse(self):
        games = parse(self.lines)
        expect = {
            1: [
                [(3, 'blue'), (4, 'red')],
                [(1, 'red'), (2, 'green'), (6, 'blue')],
                [(2, 'green')],
            ],
            2: [
                [(1, 'blue'), (2, 'green')],
                [(3, 'green'), (4, 'blue'), (1, 'red')],
                [(1, 'green'), (1, 'blue')],
            ],
            3: [
                [(8, 'green'), (6, 'blue'), (20, 'red')],
                [(5, 'blue'), (4, 'red'), (13, 'green')],
                [(5, 'green'), (1, 'red')],
            ],
            4: [
                [(1, 'green'), (3, 'red'), (6, 'blue')],
                [(3, 'green'), (6, 'red')],
                [(3, 'green'), (15, 'blue'), (14, 'red')],
            ],
            5: [
                [(6, 'red'), (1, 'blue'), (3, 'green')],
                [(2, 'blue'), (1, 'red'), (2, 'green')],
            ],
        }
        self.assertEqual(expect, games)

    def test_example_part1(self):
        games = parse(self.lines)
        contains = {
            'red': 12,
            'green': 13,
            'blue': 14,
        }
        self.assertTrue(is_possible(contains, games[1]))
        self.assertTrue(is_possible(contains, games[2]))
        self.assertTrue(is_possible(contains, games[5]))
        self.assertFalse(is_possible(contains, games[3]))
        self.assertFalse(is_possible(contains, games[4]))
        id_total = 0
        for game_id, game in games.items():
            if is_possible(contains, game):
                id_total += game_id
        self.assertEqual(id_total, 8)

    def test_example_part2(self):
        games = parse(self.lines)
        self.assertEqual(minimum_needed(games[1]), {'red': 4, 'green': 2, 'blue': 6})
        self.assertEqual(minimum_needed(games[2]), {'red': 1, 'green': 3, 'blue': 4})
        self.assertEqual(minimum_needed(games[3]), {'red': 20, 'green': 13, 'blue': 6})
        self.assertEqual(minimum_needed(games[4]), {'red': 14, 'green': 3, 'blue': 15})
        self.assertEqual(minimum_needed(games[5]), {'red': 6, 'green': 3, 'blue': 2})


game_re = re.compile(r'Game (\d+): (.*)$')

COLOR_NAMES = ('blue', 'green', 'red')

def parse_game(string):
    num, color = map(str.strip, string.split())
    assert color in COLOR_NAMES
    assert all(char.isdigit() for char in num)
    return (int(num), color)

def parse_reveal(string):
    return list(map(parse_game, string.split(',')))

def parse_reveal_sets(string):
    return list(map(parse_reveal, string.split(';')))

def parse_line(line):
    match = game_re.match(line)
    assert match
    game_id, reveal_string = match.groups()
    return (int(game_id), parse_reveal_sets(reveal_string))

def parse(lines):
    return defaultdict(list, map(parse_line, lines))

def itercubes(game):
    for reveal in game:
        for num, color in reveal:
            yield (num, color)

def count_colors(game):
    counts = defaultdict(int, zip(COLOR_NAMES, repeat(0)))
    for num, color in itercubes(game):
        counts[color] += num
    return counts

def is_possible(contains, game):
    for num, color in itercubes(game):
        if num > contains[color]:
            return False
    return True

def minimum_needed(game):
    counts = defaultdict(int)
    for num, color in itercubes(game):
        if num > counts[color]:
            counts[color] = num
    return counts

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--input',
        default = 'inputs/day02.txt',
        type = argparse.FileType(),
    )
    args = parser.parse_args(argv)

    games = parse(args.input)

    part1_contains = {
        'red': 12,
        'green': 13,
        'blue': 14,
    }
    part1_id_total = sum(
        game_id for game_id, game in games.items()
        if is_possible(part1_contains, game)
    )
    assert part1_id_total == 2149
    print(f'{part1_id_total=}')

    needed = [minimum_needed(game) for game_id, game in games.items()]
    powers = [reduce(mul, needdict.values()) for needdict in needed]
    part2_power_sum = sum(powers)
    assert part2_power_sum == 71274
    print(f'{part2_power_sum=}')

if __name__ == '__main__':
    main()
