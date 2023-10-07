import argparse
import operator
import functools
import math
import re

from collections import Counter

from least_amount_fuel import least_amount_fuel

from day08 import day08_part1
from day08 import day08_part2
from day11 import day11_part1
from day11 import day11_part2
from day12 import day12_part1
from day12 import day12_part2
from day13 import day13_part1
from day13 import day13_part2
from day14 import day14_part1
from day14 import day14_part2
from util import input_filename
from util import iter_table_indexes

class AdventOfError(Exception):
    pass


def nincreasing(numbers):
    """
    Return the number of increasing numbers.
    """
    return sum(1 for n1, n2 in zip(numbers[:-1], numbers[1:]) if n2 > n1)

def day01_data():
    """
    Lines of text of integers to list of integers.
    """
    with open(input_filename(1)) as fp:
        numbers = [int(line.strip()) for line in fp]
        return numbers

def day01_part1():
    """
    Count of increasing numbers.
    """
    numbers = day01_data()
    n = nincreasing(numbers)
    assert n == 1754, f'{n} != 1754'
    print(f'Day 1 Part 1 Solution: {n}')

def day01_part2():
    """
    Chunk into groups of sliding windows of length three; and then perform
    previous count of increasing numbers.
    """
    numbers = day01_data()
    data = {}
    for window in range(len(numbers)):
        for index in range(window, window+3):
            if index >= len(numbers):
                break
            if window not in data:
                data[window] = 0
            data[window] += numbers[index]
    values = [data[key] for key in sorted(data)]
    n = nincreasing(values)
    assert n == 1789, f'{n} != 1789'
    print(f'Day 1 Part 2 Solution: {n}')

def day02_data():
    with open(input_filename(2)) as fp:
        instructions = (line.split() for line in fp)
        instructions = [(dir, int(num)) for dir, num in instructions]
        return instructions

def navigate_submarine(instructions):
    """
    Map instructions to attributes of position and apply magnitude.
    """
    pos = {'h': 0, 'd': 0}
    map = {'forward': ('h', 1), 'down': ('d', 1), 'up': ('d', -1)}
    for direction, magnitude in instructions:
        attr, scale = map[direction]
        pos[attr] += scale * magnitude
    return pos

_day02_test = [('forward', 5), ('down', 5), ('forward', 8), ('up', 3), ('down', 8), ('forward', 2)]

def day02_part1():
    """
    Day 2 part 1 sample and challenge.
    """
    pos = navigate_submarine(_day02_test)
    n = pos['h'] * pos['d']
    assert n == 150, f'{n} != 105'

    pos = navigate_submarine(day02_data())
    n = pos['h'] * pos['d']
    assert n == 1692075
    print(f'Day 2 Part 1 Solution: {n}')

def navigate_submarine2(instructions):
    """
    More complicated submarine instruction application with 'aim' (a).
    """
    pos = {'h': 0, 'd': 0, 'a': 0}
    for direction, mag in instructions:
        if direction == 'down':
            pos['a'] += mag
        elif direction == 'up':
            pos['a'] -= mag
        elif direction == 'forward':
            pos['h'] += mag
            pos['d'] += pos['a'] * mag
        # NOTE: thought about the new match statement here, but all it does is
        #       add extra indent.
    return pos

def day02_part2():
    """
    Day 2 part 2 sample and challenge.
    """
    pos = navigate_submarine2(_day02_test)
    n = pos['h'] * pos['d']
    assert n == 900, f'{n} != 900'

    pos = navigate_submarine2(day02_data())
    n = pos['h'] * pos['d']
    assert n == 1749524700
    print(f'Day 2 Part 1 Solution: {n}')

def day03_data():
    with open(input_filename(3)) as fp:
        return [int('0b' + line.strip(), base=2) for line in fp]

def count_of(iterable):
    d = {}
    for value in iterable:
        if value not in d:
            d[value] = 0
        d[value] += 1
    return d

def sort_common(counts, n=1, reverse=False):
    # reverse = True for most common, False for least
    return sorted(counts, key=lambda k: counts[k], reverse=reverse)[:n]

def mkmasks(nbits):
    masks = [1 << shift for shift in range(nbits)]
    return masks

def nsetbits(n):
    """
    Count set bits in `n`
    """
    # no intuition for binary--had to look this up again.
    count = 0
    while n > 0:
        count += n & 1
        n >>= 1
    return count

def power_consumption(bnums, nbits):
    # should a "make masks" function generate them from most-significant to
    # least instead? we just reverse here.
    masks = mkmasks(nbits)
    masks.reverse()
    # NOTE: "first bit" in challenge refers to least significant bit (right-most).
    # separate bits into lists
    as_rows = [[int((bnum & mask) != 0) for mask in masks] for bnum in bnums]
    # make column-wise
    as_cols = list(zip(*as_rows))
    # count bits into dict
    as_cols_count = [count_of(col) for col in as_cols]
    # grab highest/lowest counts of lists of bits
    gamma_bits = [max(counts, key=lambda key: counts[key]) for counts in as_cols_count]
    epsilon_bits = [min(counts, key=lambda key: counts[key]) for counts in as_cols_count]
    # lists of bits back to number
    gamma = int('0b' + ''.join(map(str, gamma_bits)), base=2)
    epsilon = int('0b' + ''.join(map(str, epsilon_bits)), base=2)
    solution = gamma * epsilon
    return solution

_day3_sample_bnums = [
    0b00100,
    0b11110,
    0b10110,
    0b10111,
    0b10101,
    0b01111,
    0b00111,
    0b11100,
    0b10000,
    0b11001,
    0b00010,
    0b01010,
]

def day03_part1():
    """
    Day 3 part 1
    """
    solution = power_consumption(_day3_sample_bnums, 5)
    assert solution == 198, f'{solution} != 198'
    # part 1
    bnums = day03_data()
    solution = power_consumption(bnums, 12)
    assert solution == 4160394, f'{solution} != 4160394'
    print(f'Day 3 Part 1 Solution: {solution}')

def isbitset(n, k):
    return (n >> k) & 1

def bit_filtering(bnums, bitlength, most_or_least, bit_if_equal):
    if most_or_least not in ('most', 'least'):
        raise AdventOfError('most_or_least must be "most" or "least".')
    reverse = True if most_or_least == 'most' else False
    bnums = bnums[:]
    # filter by most/least common bit in a position
    while len(bnums) > 1:
        for k in range(bitlength-1, -1, -1):
            # bit at k-th position of all bnums
            bits = [n >> k & 1 for n in bnums]
            counts = count_of(bits)
            if counts[0] == counts[1]:
                # equally common
                filter_bit = bit_if_equal
            else:
                filter_bit = sort_common(counts, reverse=reverse)[0]
            bnums = [n for n in bnums if n >> k & 1 == filter_bit]
            if len(bnums) == 1:
                break
    return bnums[0]

def day03_part2():
    """
    Day 3 part 2
    """
    # sample
    oxygen_generator_rating = bit_filtering(_day3_sample_bnums, 5, 'most', 1)
    assert oxygen_generator_rating == 23, f'{oxygen_generator_rating=} != 23'
    co2_scrubber_rating = bit_filtering(_day3_sample_bnums, 5, 'least', 0)
    assert co2_scrubber_rating == 10, f'{co2_scrubber_rating=} != 10'
    life_support_rating = oxygen_generator_rating * co2_scrubber_rating
    assert life_support_rating == 230, f'{life_support_rating=} != 230'
    # challenge
    bnums = day03_data()
    oxygen_generator_rating = bit_filtering(bnums, 12, 'most', 1)
    co2_scrubber_rating = bit_filtering(bnums, 12, 'least', 0)
    life_support_rating = oxygen_generator_rating * co2_scrubber_rating
    assert life_support_rating == 4125600, f'{life_support_rating=} != 4125600'
    print(f'Day 3 part 2 Solution: {life_support_rating}')

_day04_sample = """\
7,4,9,5,11,17,23,2,0,14,21,24,10,16,13,6,15,25,12,22,18,20,8,19,3,26,1

22 13 17 11  0
 8  2 23  4 24
21  9 14 16  7
 6 10  3 18  5
 1 12 20 15 19

 3 15  0  2 22
 9 18 13 17  5
19  8  7 25 23
20 11 10 24  4
14 21 16 12  6

14 21 17 24  4
10 16 15  9 19
18  8 23 26 20
22 11 13  6  5
 2  0 12  3  7"""

class BingoCell:

    def __init__(self, value):
        self.value = value
        self.is_marked = False

    def __repr__(self):
        s = str(self.value)
        if self.is_marked:
            s += '*'
        return f'{s: >3}'


def parse_bingo_string(s):
    drawn_numbers, *boards = re.split('^$', s, flags=re.MULTILINE)
    drawn_numbers = list(map(int, drawn_numbers.split(',')))
    boards = [
        [
            list(map(BingoCell, map(int, rowline.split())))
            for rowline in board.splitlines() if rowline
        ]
        for board in boards
    ]
    return drawn_numbers, boards

def is_win_board(board):
    for row in board:
        if all(cell.is_marked for cell in row):
            return True
    for col in zip(*board):
        if all(cell.is_marked for cell in col):
            return True
    return False

def day04_data():
    with open(input_filename(4)) as fp:
        return fp.read()

def update_board(board, drawn_number):
    for row in board:
        for cell in row:
            if drawn_number == cell.value:
                cell.is_marked = True

def play_bingo(drawn_numbers, boards, last_winner=False):
    # probably should bust up between playing bingo and calculating score.
    boards = boards[:]
    winners = []
    # draw numbers, updating boards, removing winners and stopping when no
    # boards are playing.
    for drawn_number in drawn_numbers:
        todo = []
        for board in boards:
            update_board(board, drawn_number)
            if is_win_board(board):
                # leave pop(ed)
                winners.append((drawn_number, board))
                todo.append(board)
        for board in todo:
            boards.remove(board)
        if not boards:
            break
    index = 0 if not last_winner else -1
    winning_number, winner = winners[index]
    unmarked_sum = sum(cell.value for row in winner for cell in row if not cell.is_marked)
    score = winning_number * unmarked_sum
    return score

def day04_part1():
    """
    Day 4 part 1
    """
    # sample
    drawn_numbers, boards = parse_bingo_string(_day04_sample)
    winners = [board for board in boards if is_win_board(board)]
    assert len(winners) == 0, f'{len(winners)=} != 0 for initial'
    score = play_bingo(drawn_numbers, boards)
    assert score == 4512, f'{score=} != 4512'
    # challenge
    drawn_numbers, boards = parse_bingo_string(day04_data())
    score = play_bingo(drawn_numbers, boards)
    assert score == 23177, f'{score=} != 23177'
    print(f'Day 4 part 1 Solution: {score}')

def day04_part2():
    """
    Day 4 part 2
    """
    # sample
    drawn_numbers, boards = parse_bingo_string(_day04_sample)
    winners = [board for board in boards if is_win_board(board)]
    assert len(winners) == 0, f'{len(winners)=} != 0 for initial'
    score = play_bingo(drawn_numbers, boards, last_winner=True)
    assert score == 1924, f'{score=} != 1924'
    # challenge
    drawn_numbers, boards = parse_bingo_string(day04_data())
    score = play_bingo(drawn_numbers, boards, last_winner=True)
    assert score == 6804, f'{score=} != 6804'
    print(f'Day 4 part 2 Solution: {score}')

_day05_sample = """\
0,9 -> 5,9
8,0 -> 0,8
9,4 -> 3,4
2,2 -> 2,1
7,0 -> 7,4
6,4 -> 2,0
0,9 -> 2,9
3,4 -> 1,4
0,0 -> 8,8
5,5 -> 8,2"""

def strtupint(s):
    return tuple(map(int, s.split(',')))

def parse_line_segments_string(s):
    line_segments = []
    for textline in s.splitlines():
        p1, p2 = textline.split(' -> ')
        p1 = strtupint(p1)
        p2 = strtupint(p2)
        line_segments.append((p1, p2))
    return line_segments

def is_flat(p1, p2):
    """
    The line segment is flat horizontally or vertically.
    """
    return p1[0] == p2[0] or p1[1] == p2[1]

def walk_line(p1, p2):
    """
    Generate points along a line segment that is flat horizontally or
    vertically; or is perfectly diagonal.
    """
    x, y = p1
    if p2[0] != x:
        dx = int(math.copysign(1, p2[0] - x))
    else:
        dx = 0
    if p2[1] != y:
        dy = int(math.copysign(1, p2[1] - y))
    else:
        dy = 0
    while (x,y) != p2:
        yield (x, y)
        x += dx
        y += dy
    yield p2

def day05_data():
    with open(input_filename(5)) as fp:
        return fp.read()

def count_lines_overlap(line_segments_string, only_flat=True):
    line_segments = parse_line_segments_string(line_segments_string)
    if only_flat:
        line_segments = [seg for seg in line_segments if is_flat(*seg)]
    grid = Counter(pos for seg in line_segments for pos in walk_line(*seg))
    n = sum(1 for key, count in grid.items() if count > 1)
    return n

def day05_part1():
    """
    Day 5 part 1
    """
    # only considers flat lines
    # sample
    n = count_lines_overlap(_day05_sample)
    assert n == 5, f'{n=} != 5'
    # challenge
    n = count_lines_overlap(day05_data())
    assert n == 5197, f'{n=} != 5197'
    print(f'Day 5 Part 1 Solution: {n}')

def day05_part2():
    """
    Day 5 part 2
    """
    # includes diagonals
    # sample
    n = count_lines_overlap(_day05_sample, only_flat=False)
    assert n == 12
    # challenge
    n = count_lines_overlap(day05_data(), only_flat=False)
    assert n == 18605, f'{n=} != 18605'
    print(f'Day 5 Part 2 Solution: {n}')

_day06_sample = [3,4,3,1,2]

def day06_data():
    with open(input_filename(6)) as fp:
        fishes = fp.read()
        return list(map(int, fishes.split(',')))

def simulate_lanternfish_naive(ndays, fishes):
    fishes = fishes[:]
    for day in range(ndays+1):
        for index in range(len(fishes)):
            if fishes[index] < 0:
                fishes.append(8)
                fishes[index] = 6
        # XXX
        # this seems like it's doing two days but it works for the sample and
        # part 1.
        for index in range(len(fishes)):
            fishes[index] -= 1
    return fishes

def day06_part1():
    """
    Day 6 part 1
    """
    fishes = simulate_lanternfish_naive(80, _day06_sample)
    n = len(fishes)
    assert n == 5934, f'{n=} != 5934'
    fishes = day06_data()
    n = len(simulate_lanternfish_naive(80, fishes))
    assert n == 385391, f'{n=} != 385391'
    print(f'Day 6 Part 1 Solution: {n}')

def day06_cheat(ndays, fish_timers):
    # https://zonito.medium.com/lantern-fish-day-6-advent-of-code-2021-python-solution-4444387a8380
    # TODO: understand this
    """
    from the website using the sample data

    [3, 4, 3, 1, 2]

    The days list on loop n:
              0    1   2   3   4   5   6   7   8

    fish_timer = 0
    index = (0 + 7) % 9 = 7
    loop 0:  [0,   1,  1,  2,  1,  0,  0,  0,  0]

    i = 10
    fish_timer = 10 % 9 = 1
    index = (fish_timer + 7) % 9 = (1 + 7) % 9 = 8 % 9 = 8
    days[index] += days[1]

                  +2  +1              +1  +1  +1
    loop 10: [1,   3,  2,  2,  1,  0,  1,  1,  1]
    loop 25: [1,   3,  2,  2,  1,  0,  1,  1,  1]

    loop 50: [56, 41, 84, 23, 51, 36, 56, 44, 44]
                                  +
                                  |
                           +------+
                           |
                           v
                         +36
    loop 51: [56, 41, 84, 59, 51, 36, 56, 44, 44]

    Study this link:
    https://cestlaz.github.io/post/advent-2021-day06/
    it looks like a better explanation of the [0]*9 structure above.
    """
    days = [0] * 9

    # the indexes of `days` is a fish timer. there are nine because of the
    # extra two days a new fish takes to start producing.
    for fish_timer in fish_timers:
        days[fish_timer] += 1

    # iterate the number of days
    for i in range(ndays):
        fish_timer = i % 9
        index = (fish_timer + 7) % 9
        days[index] += days[fish_timer]

    total_fish = sum(days)
    return total_fish

def day06_part2():
    """
    Day 6 part 2
    """
    n = day06_cheat(256, _day06_sample)
    assert n == 26984457539, f'{n=} != 26984457539'
    return
    fishes = day06_data()
    fishes = simulate_lanternfish_naive(80, fishes)
    n = len(fishes)
    assert n == 385391, f'{n=} != 385391'
    print(f'Day 6 Part 1 Solution: {n}')

_day07_sample = [16,1,2,0,4,2,7,1,2,14]

def day07_data():
    with open(input_filename(7)) as fp:
        return list(map(int, fp.read().split(',')))

def absdiff(p1, p2):
    return abs(p1 - p2)

def day07_part1():
    """
    Day 7 Part 1
    """
    # NOTE: function in another module
    fuel = least_amount_fuel(_day07_sample, costfunc=absdiff)
    assert fuel == 37, f'{fuel=} != 37'
    hpos = day07_data()
    fuel = least_amount_fuel(hpos, costfunc=absdiff)
    assert fuel == 345035, f'{fuel=} != 345035'
    print(f'Day 7 Part 1 Solution: {fuel}')

# lru_cache shaved about 5 seconds off part 2, down to 15s
@functools.lru_cache(maxsize=None)
def increasing_move_cost(p1, p2):
    return sum(1+i for i in range(abs(p1-p2)))

def increasing_move_cost(p1, p2):
    """
    here we go, this got the speed up:
    $ time python adventofcode.py day07 2
    Day 7 Part 2 Solution: 97038163

    real	0m0.230s
    user	0m0.212s
    sys	0m0.003s

    On an AMD Ryzen 7 2700X Eight-Core Processor

    Apparently this is attributed to a young Gauss but there seems to be some dispute.

    Need to remember how to sum numbers from 1 to n
    n(n+1)
    ------
       2

    notice there are n/2 * n+1 by grouping the sums by first and last, second
    and second-to-last, etc.

    1, 2, 3, ..., n-2, n-1, n
    |  |  |       |    |    |
    |  |  +- n+1 -+    |    |
    |  +---- n+1 ------+    |
    +------- n+1 -----------+
    """
    n = abs(p1 - p2)
    return (n * (n + 1)) // 2

def day07_part2():
    """
    Day 7 Part 2
    """
    # NOTE: function in another module
    fuel = least_amount_fuel(_day07_sample, costfunc=increasing_move_cost)
    assert fuel == 168, f'{fuel=} != 168'
    hpos = day07_data()
    fuel = least_amount_fuel(hpos, costfunc=increasing_move_cost)
    assert fuel == 97038163, f'{fuel=} != 97038163'
    print(f'Day 7 Part 2 Solution: {fuel}')

_day09_example = """\
2199943210
3987894921
9856789892
8767896789
9899965678"""

def parse_height_map(s):
    return list(list(map(int, line)) for line in s.splitlines())

def adjacent_height_indexes(heightmap, row, col):
    # top, right, bottom, left
    if row-1 >= 0:
        yield row-1, col
    if col+1 < len(heightmap[0]):
        yield row, col + 1
    if row+1 < len(heightmap):
        yield row+1, col
    if col-1 >= 0:
        yield row, col - 1

def tables_match(t1, t2):
    assert len(t1) == len(t2)
    for r1, r2 in zip(t1, t2):
        assert len(r1) == len(r2)
    for r, c in iter_table_indexes(t1):
        if t1[r][c] != t2[r][c]:
            return False
    return True

def iterate_height_map(heightmap):
    for rowi, row in enumerate(heightmap):
        for coli, height in enumerate(row):
            yield ((rowi, coli), height)

def compute_risk_level(heightmap):
    lowest = []
    for ((r, c), height) in iterate_height_map(heightmap):
        if all(
            height < heightmap[adjrow][adjcol]
            for adjrow, adjcol in adjacent_height_indexes(heightmap, r, c)
        ):
            lowest.append(((r,c), height))
    risk_level = sum(height+1 for _, height in lowest)
    return risk_level

def day09_data():
    with open(input_filename(9)) as fp:
        return fp.read()

def day09_part1():
    """
    Day 9 Part 1
    """
    # example
    heightmap = parse_height_map(_day09_example)
    risk_level = compute_risk_level(heightmap)
    assert risk_level == 15, f'{risk_level=} != 15'
    # challenge
    heightmap = parse_height_map(day09_data())
    risk_level = compute_risk_level(heightmap)
    assert risk_level == 468, f'{risk_level=} != 468'
    print(f'Day 9 Part 1 Solution: {risk_level=}')

def flood(heightmap, pos, parent=None):
    result = [[None for col in row ] for row in heightmap]
    q = []
    r, c = pos
    height = heightmap[r][c]
    if height < 9:
        result[r][c] = height
        q.append(pos)
    while q:
        r, c = q.pop()
        for adjr, adjc in adjacent_height_indexes(heightmap, r, c):
            height = heightmap[adjr][adjc]
            if height < 9 and result[adjr][adjc] is None:
                result[adjr][adjc] = height
                q.append((adjr, adjc))
    return result

def basin_size(basin):
    return sum(1 for row in basin for col in row if col is not None)

def get_basins(heightmap):
    basins = []
    for pos, _ in iterate_height_map(heightmap):
        basin = flood(heightmap, pos)
        size = basin_size(basin)
        if size > 0 and not any(tables_match(basin, existing) for existing in basins):
            basins.append(basin)
    return basins

def basins_result(basins):
    top_three = sorted(basins, key=basin_size)[-3:]
    result = functools.reduce(operator.mul, map(basin_size, top_three))
    return result

def day09_part2():
    """
    Day 9 Part 2
    """
    # example
    heightmap = parse_height_map(_day09_example)
    basins = get_basins(heightmap)
    result = basins_result(basins)
    assert result == 1134, f'{result=} != 1134'
    # challenge
    heightmap = parse_height_map(day09_data())
    basins = get_basins(heightmap)
    result = basins_result(basins)
    assert result == 1280496, f'{result=} != 1280496'
    print(f'Day 9 Part 2 Solution: {result=}')
    # XXX
    # This took five minutes
    # * better way to check existing?
    # * avoid column/row nesting?
    #
    # $ time python adventofcode.py day09 2
    # Day 9 Part 2 Solution: result=1280496
    #
    # real	5m8.441s
    # user	5m7.902s
    # sys	0m0.053s

_day10_example = """\
[({(<(())[]>[[{[]{<()<>>
[(()[<>])]({[<{<<[]>>(
{([(<{}[<>[]}>{[]{[(<()>
(((({<>}<{<{<>}{[]{[]{}
[[<[([]))<([[{}[[()]]]
[{[{({}]{}}([{[{{{}}([]
{<[[]]>}<{[{[{[]{()[[[]
[<(<(<(<{}))><([]([]()
<{([([[(<>()){}]>(<<{{
<{([{{}}[<[[[<>{}]]]>[]]"""

opens = '([{<'
closes = ')]}>'
closes_points = {')': 3, ']': 57, '}': 1197, '>': 25137}
completer_points = {closer:points for points,closer in enumerate(closes, start=1)}

class Day10Corrupted(Exception):

    def __init__(self, opener, corrupter):
        self.opener = opener
        self.corrupter = corrupter

    def __str__(self):
        expected = closes[opens.index(self.opener)]
        return f'Expected {expected} but found {self.corrupter} instead.'


def process_syntax(line):
    """
    Process a line of openers and closers, raising for corrupted closers. If no
    corrupted closers, return incomplete openers.
    """
    q = []
    for char in line:
        if char in opens:
            q.append(char)
        elif char in closes:
            closer = char
            opener = q.pop()
            if closes.index(closer) != opens.index(opener):
                raise Day10Corrupted(opener=opener, corrupter=closer)
    incomplete = q
    return incomplete

def get_corrupted(lines):
    """
    Capture and return the corrupted lines--incorrect closing character.
    """
    corrupted = []
    for line in lines.splitlines():
        try:
            process_syntax(line)
        except Day10Corrupted as e:
            corrupted.append(e)
    return corrupted

def get_incomplete(lines):
    """
    Process all syntax lines, ignoring corrupted exceptions, and returning the
    incomplete openers.
    """
    incompletes = []
    for line in lines.splitlines():
        try:
            incomplete = process_syntax(line)
        except Day10Corrupted:
            # ignore corrupted
            pass
        else:
            if incomplete:
                incompletes.append(incomplete)
    return incompletes

def get_corrupted_points(string):
    """
    Calculate points from corrupted closers for all lines in `string`.
    """
    corrupted = get_corrupted(string)
    points = sum(closes_points[error.corrupter] for error in corrupted)
    return points

def day10_part1():
    """
    Day 10 Part 1
    """
    # example
    points = get_corrupted_points(_day10_example)
    assert points == 26397, f'{points=} != 26397'
    # challenge
    string = open(input_filename(10)).read()
    points = get_corrupted_points(string)
    assert points == 462693, f'{points=} != 462693'
    print(f'Day 10 Part 1 Solution: {points=}')

def score_completers(completers):
    """
    Calculate the score from characters that would complete the incomplete
    openers for a single syntax line.
    """
    score = 0
    for closer in completers:
        p = completer_points[closer]
        score *= 5
        score += p
    return score

def get_score_for_completion(string):
    """
    Calculate the total score for completers from all lines of syntax `string`.
    The score is the middle element of the list of points for the lines in
    `string`.
    """
    incompletes_for_lines = get_incomplete(string)
    points = []
    for incompletes in incompletes_for_lines:
        completes = []
        while incompletes:
            incomchar = incompletes.pop()
            comchar = closes[opens.index(incomchar)]
            completes.append(comchar)
        score = score_completers(completes)
        points.append(score)
    points = sorted(points)
    middle = points[len(points)//2]
    return middle

def day10_part2():
    """
    Day 10 Part 2
    """
    # example
    middle = get_score_for_completion(_day10_example)
    assert middle == 288957, f'{middle=} != 288957'
    # challenge
    string = open(input_filename(10)).read()
    middle = get_score_for_completion(string)
    assert middle == 3094671161, f'{middle=} != 3094671161'
    print(f'Day 10 Part 2 Solution: {middle=}')

def runall(args):
    _func_re = re.compile('day\d{2}_part\d')
    funcs = []
    for name in globals():
        if _func_re.match(name):
            funcs.append(name)

    funcs.sort()
    for funcname in funcs:
        try:
            globals()[funcname]()
        except NotImplementedError as e:
            print(e)

def runday(args):
    funcname = f'day{args.day:02d}_part{args.part}'
    try:
        func = globals()[funcname]
    except KeyError:
        raise AdventOfError(f'command {funcname} not found.')
    func()

def main(argv=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser_all = subparsers.add_parser('all')
    parser_all.set_defaults(func=runall)
    parser_day = subparsers.add_parser('day')
    parser_day.add_argument('day', type=int)
    parser_day.add_argument('part', choices=[1,2], type=int)
    parser_day.set_defaults(func=runday)
    args = parser.parse_args(argv)

    args = vars(args)
    func = args['func']
    del args['func']
    func(argparse.Namespace(**args))

if __name__ == '__main__':
    main()
