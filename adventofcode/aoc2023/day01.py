import argparse
import unittest

# https://adventofcode.com/2023/day/1

part1_text = """
--- Day 1: Trebuchet?! ---

Something is wrong with global snow production, and you've been selected to
take a look. The Elves have even given you a map; on it, they've used stars to
mark the top fifty locations that are likely to be having problems.

You've been doing this long enough to know that to restore snow operations, you
need to check all fifty stars by December 25th.

Collect stars by solving puzzles. Two puzzles will be made available on each
day in the Advent calendar; the second puzzle is unlocked when you complete the
first. Each puzzle grants one star. Good luck!

You try to ask why they can't just use a weather machine ("not powerful
enough") and where they're even sending you ("the sky") and why your map looks
mostly blank ("you sure ask a lot of questions") and hang on did you just say
the sky ("of course, where do you think snow comes from") when you realize that
the Elves are already loading you into a trebuchet ("please hold still, we need
to strap you in").

As they're making the final adjustments, they discover that their calibration
document (your puzzle input) has been amended by a very young Elf who was
apparently just excited to show off her art skills. Consequently, the Elves are
having trouble reading the values on the document.

The newly-improved calibration document consists of lines of text; each line
originally contained a specific calibration value that the Elves now need to
recover. On each line, the calibration value can be found by combining the
first digit and the last digit (in that order) to form a single two-digit
number.

For example:

1abc2
pqr3stu8vwx
a1b2c3d4e5f
treb7uchet

In this example, the calibration values of these four lines are 12, 38, 15, and
77. Adding these together produces 142.

Consider your entire calibration document. What is the sum of all of the
calibration values?
"""

part2_text = """
Your calculation isn't quite right. It looks like some of the digits are
actually spelled out with letters: one, two, three, four, five, six, seven,
eight, and nine also count as valid "digits".

Equipped with this new information, you now need to find the real first and
last digit on each line. For example:

two1nine
eightwothree
abcone2threexyz
xtwone3four
4nineeightseven2
zoneight234
7pqrstsixteen

In this example, the calibration values are 29, 83, 13, 24, 42, 14, and 76.
Adding these together produces 281.
"""

class Tests(unittest.TestCase):

    def test_part1_example(self):
        example_lines = [
            '1abc2',
            'pqr3stu8vwx',
            'a1b2c3d4e5f',
            'treb7uchet',
        ]
        result = sum(solve(line, []) for line in example_lines)
        self.assertEqual(result, 142)
        # test with names because there are no names in this example
        result = sum(solve(line, NUMBERS) for line in example_lines)
        self.assertEqual(result, 142)

    def test_part2_example(self):
        example_lines = [
            'two1nine',
            'eightwothree',
            'abcone2threexyz',
            'xtwone3four',
            '4nineeightseven2',
            'zoneight234',
            '7pqrstsixteen',
        ]
        expect_numbers = [29, 83, 13, 24, 42, 14, 76]
        calibrations = [solve(line, NUMBERS) for line in example_lines]
        for expected, actual in zip(expect_numbers, calibrations):
            self.assertEqual(expected, actual)
        self.assertEqual(sum(calibrations), 281)


NUMBERS = [
    'one',
    'two',
    'three',
    'four',
    'five',
    'six',
    'seven',
    'eight',
    'nine',
]

def solve(line, names):
    for n, name in enumerate(names, start=1):
        line = line.replace(name, f'{name[0]}{n}{name[-1]}')
    digits = [char for char in line if char.isdigit()]
    if len(digits) < 2:
        digits += digits
    return int(digits[0] + digits[-1])

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--input',
        default = 'inputs/day01.txt',
        type = argparse.FileType(),
    )
    args = parser.parse_args(argv)

    with args.input as input_file:
        lines = [line.strip() for line in input_file]
        # confirm all lowercase
        assert all(char.islower() for line in lines for char in line if char.isalpha())

    part1_answer = sum(solve(line, []) for line in lines)
    assert part1_answer == 54390
    print(f'{part1_answer=}')

    part2_answer = sum(solve(line, NUMBERS) for line in lines)
    assert part2_answer == 54277
    print(f'{part2_answer=}')
    # incorrect:
    # - 0 (zero)
    # - 54305
    # - 54390
    # - 54341

if __name__ == '__main__':
    main()

# 2023-12-01
# - tried lots of things
# - should set up a test case for when one integer name bleeds into the next,
#   depending on which direction you're scanning the string
#   - this is likely the problem with my attempts
# - finally just used the juanplopes_day01.py solution
# - https://www.reddit.com/r/adventofcode/comments/1883ibu/2023_day_1_solutions/kbk7rxh/
# - https://github.com/juanplopes/advent-of-code-2023/blob/main/day01.py
# - like the idea of passing the names list to handle both cases
# - never would have thought of replacing the middle of the digit names
#   - suspect this keeps replacements unique
# - didn't care for using `ord` to get an integer
# - didn't care for using less-than-or-equal when `isdigit` exists
# - don't think there are ever no digits, so removed that test
# - just leave as strings and concat and convert at end
