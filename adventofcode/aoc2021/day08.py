from collections import Counter

from util import input_filename

_day08_example = """\
be cfbegad cbdgef fgaecd cgeb fdcge agebfd fecdb fabcd edb | fdgacbe cefdb cefbgd gcbe
edbfga begcd cbg gc gcadebf fbgde acbgfd abcde gfcbed gfec | fcgedb cgb dgebacf gc
fgaebd cg bdaec gdafb agbcfd gdcbef bgcad gfac gcb cdgabef | cg cg fdcagb cbg
fbegcd cbd adcefb dageb afcb bc aefdc ecdab fgdeca fcdbega | efabcd cedba gadfec cb
aecbfdg fbg gf bafeg dbefa fcge gcbea fcaegb dgceab fcbdga | gecf egdcabf bgf bfgea
fgeab ca afcebg bdacfeg cfaedg gcfdb baec bfadeg bafgc acf | gebdcfa ecba ca fadegcb
dbcfg fgd bdegcaf fgec aegbdf ecdfab fbedc dacgb gdcebf gf | cefg dcbef fcge gbcadfe
bdfegc cbegaf gecbf dfcage bdacg ed bedf ced adcbefg gebcd | ed bcgafe cdgba cbgef
egadfb cdbfeg cegd fecab cgb gbdefca cg fgcdab egfdb bfceg | gbdfcae bgc cg cgb
gcafb gcf dcaebfg ecagb gf abcdeg gaef cafbge fdbac fegbdc | fgae cfgab fg bagce"""

# digit: n segments used to display
digit_nsegs = {0: 6, 1: 2, 2: 5, 3: 5, 4: 4, 5: 5, 6: 6, 7: 3, 8: 7, 9: 6}
nsegs_digit = dict(map(reversed, digit_nsegs.items()))

# numbers of segments that are unique
unique_nsegs = {
    nsegs
    for nsegs, count in Counter(digit_nsegs.values()).items()
    if count == 1
}

# map unique number of segments back to digit
unique_nsegs_to_digit = {
    unique_nsegs: nsegs_digit[unique_nsegs]
    for unique_nsegs in unique_nsegs
}

def parse_seven_segment_display_line(s):
    signals, output_values = s.split('|')
    signals = [pattern for pattern in signals.split() if pattern]
    output_values = [value for value in output_values.split() if value]
    return (signals, output_values)

def generate_signals(signal_string):
    nunique = 0
    for line in signal_string.splitlines():
        item = parse_seven_segment_display_line(line)
        yield item

def day08_data():
    with open(input_filename(8)) as fp:
        return fp.read()

def count_unique_signals(signal_string):
    nunique = 0
    for item in generate_signals(signal_string):
        signals, output_values = item
        for signal in output_values:
            lenseg = len(signal)
            if lenseg in unique_nsegs:
                digit = unique_nsegs_to_digit[lenseg]
                nunique += 1
    return nunique

def must_be_digit_by_unique(signal_string):
    mappings = []
    for item in generate_signals(signal_string):
        input_signals, output_values = item
        # LEFT OFF HERE


        for signal in output_values:

            mappings.append((signals, output_values, get_mapping(signals, output_values)))

            lenseg = len(signal)
            if lenseg in unique_nsegs:
                digit = unique_nsegs_to_digit[lenseg]
                signals[signal] = digit
    return signals

def get_mapping(signals, output):
    pass

def day08_part1():
    """
    Day 8 Part 1
    """
    # example
    n = count_unique_signals(_day08_example)
    assert n == 26, f'{n=} != 26'
    # challenge
    n_unique_line_segments = count_unique_signals(day08_data())
    assert n_unique_line_segments == 362, f'{n_unique_line_segments=} != 362'
    print(f'Day 8 Part 1 Solution: {n_unique_line_segments=}')

def day08_part2():
    """
    Day 8 Part 2
    """
    raise NotImplementedError
