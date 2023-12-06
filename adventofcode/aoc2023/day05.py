import argparse
import re
import textwrap
import unittest

from collections import defaultdict
from itertools import groupby
from itertools import pairwise

part1_text = """
--- Day 5: If You Give A Seed A Fertilizer ---

You take the boat and find the gardener right where you were told he would be:
managing a giant "garden" that looks more to you like a farm.

"A water source? Island Island is the water source!" You point out that Snow
Island isn't receiving any water.

"Oh, we had to stop the water because we ran out of sand to filter it with!
Can't make snow with dirty water. Don't worry, I'm sure we'll get more sand
soon; we only turned off the water a few days... weeks... oh no." His face
sinks into a look of horrified realization.

"I've been so busy making sure everyone here has food that I completely forgot
to check why we stopped getting more sand! There's a ferry leaving soon that is
headed over in that direction - it's much faster than your boat. Could you
please go check it out?"

You barely have time to agree to this request when he brings up another. "While
you wait for the ferry, maybe you can help us with our food production problem.
The latest Island Island Almanac just arrived and we're having trouble making
sense of it."

The almanac (your puzzle input) lists all of the seeds that need to be planted.
It also lists what type of soil to use with each kind of seed, what type of
fertilizer to use with each kind of soil, what type of water to use with each
kind of fertilizer, and so on. Every type of seed, soil, fertilizer and so on
is identified with a number, but numbers are reused by each category - that is,
soil 123 and fertilizer 123 aren't necessarily related to each other.

For example:

seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4

The almanac starts by listing which seeds need to be planted:

    seeds 79, 14, 55, and 13.

The rest of the almanac contains a list of maps which describe how to convert
numbers from a source category into numbers in a destination category. That is,
the section that starts with seed-to-soil map: describes how to convert a seed
number (the source) to a soil number (the destination). This lets the gardener
and his team know which soil to use with which seeds, which water to use with
which fertilizer, and so on.

Rather than list every source number and its corresponding destination number
one by one, the maps describe entire ranges of numbers that can be converted.
Each line within a map contains three numbers: the destination range start, the
source range start, and the range length.

Consider again the example seed-to-soil map:

50 98 2
52 50 48

The first line has a destination range start of 50, a source range start of 98,
and a range length of 2. This line means that the source range starts at 98 and
contains two values: 98 and 99. The destination range is the same length, but
it starts at 50, so its two values are 50 and 51. With this information, you
know that seed number 98 corresponds to soil number 50 and that seed number 99
corresponds to soil number 51.

The second line means that the source range starts at 50 and contains 48
values: 50, 51, ..., 96, 97. This corresponds to a destination range starting
at 52 and also containing 48 values: 52, 53, ..., 98, 99. So, seed number 53
corresponds to soil number 55.

Any source numbers that aren't mapped correspond to the same destination
number. So, seed number 10 corresponds to soil number 10.

So, the entire list of seed numbers and their corresponding soil numbers looks
like this:

seed  soil
0     0
1     1
...   ...
48    48
49    49
50    52
51    53
...   ...
96    98
97    99
98    50
99    51

With this map, you can look up the soil number required for each initial seed
number:

    Seed number 79 corresponds to soil number 81.
    Seed number 14 corresponds to soil number 14.
    Seed number 55 corresponds to soil number 57.
    Seed number 13 corresponds to soil number 13.

The gardener and his team want to get started as soon as possible, so they'd
like to know the closest location that needs a seed. Using these maps, find the
lowest location number that corresponds to any of the initial seeds. To do
this, you'll need to convert each seed number through other categories until
you can find its corresponding location number. In this example, the
corresponding types are:

    Seed 79, soil 81, fertilizer 81, water 81, light 74, temperature 78,
    humidity 78, location 82.

    Seed 14, soil 14, fertilizer 53, water 49, light 42, temperature 42,
    humidity 43, location 43.

    Seed 55, soil 57, fertilizer 57, water 53, light 46, temperature 82,
    humidity 82, location 86.

    Seed 13, soil 13, fertilizer 52, water 41, light 34, temperature 34,
    humidity 35, location 35.

So, the lowest location number in this example is 35.

What is the lowest location number that corresponds to any of the initial seed
numbers?
"""

part2_text = """
--- Part Two ---

Everyone will starve if you only plant such a small number of seeds. Re-reading
the almanac, it looks like the seeds: line actually describes ranges of seed
numbers.

The values on the initial seeds: line come in pairs. Within each pair, the
first value is the start of the range and the second value is the length of the
range. So, in the first line of the example above:

seeds: 79 14 55 13

This line describes two ranges of seed numbers to be planted in the garden. The
first range starts with seed number 79 and contains 14 values: 79, 80, ..., 91,
92. The second range starts with seed number 55 and contains 13 values: 55, 56,
..., 66, 67.

Now, rather than considering four seed numbers, you need to consider a total of
27 seed numbers.

In the above example, the lowest location number can be obtained from seed
number 82, which corresponds to soil 84, fertilizer 84, water 84, light 77,
temperature 45, humidity 46, and location 46. So, the lowest location number is
46.

Consider all of the initial seed numbers listed in the ranges on the first line
of the almanac. What is the lowest location number that corresponds to any of
the initial seed numbers?
"""

class Tests(unittest.TestCase):

    example_string = textwrap.dedent("""
        seeds: 79 14 55 13

        seed-to-soil map:
        50 98 2
        52 50 48

        soil-to-fertilizer map:
        0 15 37
        37 52 2
        39 0 15

        fertilizer-to-water map:
        49 53 8
        0 11 42
        42 0 7
        57 7 4

        water-to-light map:
        88 18 7
        18 25 70

        light-to-temperature map:
        45 77 23
        81 45 19
        68 64 13

        temperature-to-humidity map:
        0 69 1
        1 0 69

        humidity-to-location map:
        60 56 37
        56 93 4""")

    def test_parse_range_map(self):
        self.assertEqual(
            parse_range_map('50 98 2'),
            (seedrange(98,2), seedrange(50,2))
        )
        self.assertEqual(
            parse_range_map('52 50 48'),
            (seedrange(50,48), seedrange(52,48))
        )

    def _example_data(self):
        file_like = iter(self.example_string.splitlines(keepends=True))
        return parse(file_like)

    def test_parse(self):
        seeds, mappings = self._example_data()
        self.assertEqual(seeds, [79, 14, 55, 13])
        self.assertEqual(
            mappings[('seed', 'soil')],
            [
                (seedrange(98,2), seedrange(50,2)),
                (seedrange(50,48), seedrange(52,48)),
            ]
        )
        self.assertEqual(
            mappings[('soil', 'fertilizer')],
            [
                (seedrange(15,37), seedrange(0,37)),
                (seedrange(52,2), seedrange(37,2)),
                (seedrange(0,15), seedrange(39,15)),
            ]
        )
        self.assertEqual(
            mappings[('fertilizer', 'water')],
            [
                (seedrange(53,8), seedrange(49,8)),
                (seedrange(11,42), seedrange(0,42)),
                (seedrange(0,7), seedrange(42,7)),
                (seedrange(7,4), seedrange(57,4)),
            ]
        )
        self.assertEqual(
            mappings[('water', 'light')],
            [
                (seedrange(18,7), seedrange(88,7)),
                (seedrange(25,70), seedrange(18,70)),
            ]
        )
        self.assertEqual(
            mappings[('light', 'temperature')],
            [
                (seedrange(77,23), seedrange(45,23)),
                (seedrange(45,19), seedrange(81,19)),
                (seedrange(64,13), seedrange(68,13)),
            ]
        )
        self.assertEqual(
            mappings[('temperature', 'humidity')],
            [
                (seedrange(69,1), seedrange(0,1)),
                (seedrange(0,69), seedrange(1,69)),
            ]
        )
        self.assertEqual(
            mappings[('humidity', 'location')],
            [
                (seedrange(56,37), seedrange(60,37)),
                (seedrange(93,4), seedrange(56,4)),
            ]
        )

    def test_example1(self):
        seeds, mappings = self._example_data()
        self.assertEqual(nearest_location(seeds, mappings), 35)

    def test_example1_with_faster(self):
        seeds, mappings = self._example_data()
        self.assertEqual(nearest_location2(seeds, mappings), 35)

    def test_seeds_as_ranges(self):
        seeds, mappings = self._example_data()
        self.assertEqual(
            list(seeds_as_ranges(seeds)),
            [seedrange(79,14), seedrange(55,13)]
        )

    def test_example2(self):
        seeds, mappings = self._example_data()
        seeds = (seed for seedrange in seeds_as_ranges(seeds) for seed in seedrange)
        self.assertEqual(nearest_location(seeds, mappings), 46)

    def __test_flatten_mappings(self):
        seeds, mappings = self._example_data()
        flatten_mappings(mappings)


class ParseError(Exception):
    pass


class AOCError(Exception):
    pass


def splitint(s):
    return map(int, s.split())

def parse_range_map(line):
    dest_range_start, source_range_start, length = splitint(line)
    source_range = range(source_range_start, source_range_start + length)
    dest_range = range(dest_range_start, dest_range_start + length)
    assert len(source_range) == len(dest_range)
    return (source_range, dest_range)

mapline_re = re.compile(r'([a-z]+)-to-([a-z]+)')

def parse(input_file):
    for line in input_file:
        if line.startswith('seeds: '):
            seeds = list(splitint(line[7:]))
            break
    else:
        raise ParseError('seeds line not found')

    mappings = defaultdict(list)
    for line in input_file:
        if not line.strip():
            # skip empty lines
            continue
        match = mapline_re.match(line)
        if not match:
            raise ParseError('expected source-to-dest line')
        mapkey = match.groups()
        for line in input_file:
            if not line.strip():
                break
            mapranges = parse_range_map(line)
            srcrange, dstrange = mapranges
            mappings[mapkey].append(mapranges)
    return (seeds, mappings)

def seedrange(start, length):
    return range(start, start+length)

def seeds_as_ranges(seeds):
    def groupkey(seed):
        return seeds.index(seed) // 2

    for _, rangeargs in groupby(seeds, key=groupkey):
        yield seedrange(*rangeargs)

def chainmappings(source_id, mappings, type_='seed'):
    for typekey, rangepairs in mappings.items():
        srctype, dsttype = typekey
        if srctype == type_:
            break
    else:
        # end of chained mappings
        return

    for rangepair in rangepairs:
        srcrange, dstrange = rangepair
        if source_id in srcrange:
            dstid = dstrange[srcrange.index(source_id)]
            break
    else:
        dstid = source_id
    yield (typekey, source_id, dstid)
    if dsttype in (srctype for srctype, dsttype in mappings):
        yield from chainmappings(dstid, mappings, dsttype)

def get_location(seed, mappings):
    for typekey, srcid, dstid in chainmappings(seed, mappings):
        srctype, dsttype = typekey
        if dsttype == 'location':
            yield dstid

def nearest_location(seeds, mappings):
    min_location = None
    for seed in seeds:
        _min_locations = min(get_location(seed, mappings))
        if min_location is None or _min_locations < min_location:
            min_location = _min_locations
    return min_location

mappings_keys = [
    ('seed', 'soil'),
    ('soil', 'fertilizer'),
    ('fertilizer', 'water'),
    ('water', 'light'),
    ('light', 'temperature'),
    ('temperature', 'humidity'),
    ('humidity', 'location'),
]

def get_location2(seed, mappings):
    for cache, rangemaps_list in mappings:
        if seed not in cache:
            for rangemaps in rangemaps_list:
                srcrange, dstrange = rangemaps
                if seed in srcrange:
                    srcindex = srcrange.index(seed)
                    cache[seed] = dstrange[srcindex]
                    break
            else:
                cache[seed] = seed
        seed = cache[seed]
    return seed

def nearest_location2(seeds, mappings):
    # killed, probably memory
    # need faster without memory
    faster_mappings = [({}, mappings[mapkey]) for mapkey in mappings_keys]
    min_location = None
    for seed in seeds:
        location = get_location2(seed, faster_mappings)
        if min_location is None or location < min_location:
            min_location = location
    return min_location

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input',
        default = 'instance/inputs/day05.txt',
        type = argparse.FileType(),
    )
    args = parser.parse_args(argv)

    with args.input as input_file:
        seeds, mappings = parse(input_file)

    part1_answer = nearest_location(seeds, mappings)
    part1_answer = nearest_location2(seeds, mappings)

    assert part1_answer == 265018614
    print(f'{part1_answer=}')

    seeds = (seed for seedrange in seeds_as_ranges(seeds) for seed in seedrange)
    #part2_answer = nearest_location(seeds, mappings)
    # with slow, recursive, first try
    # real 440m26.284s
    # user 439m29.218s
    # sys  0m2.484s
    assert part2_answer == 63179500
    print(f'{part2_answer=}')

if __name__ == '__main__':
    main()
