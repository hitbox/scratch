import re

from collections import Counter
from collections import deque

from util import readinput

_day14_example = '''\
NNCB

CH -> B
HH -> N
CB -> H
NH -> C
HB -> C
HC -> B
HN -> C
NN -> C
BH -> H
NC -> B
NB -> B
BN -> B
BB -> N
BC -> B
CC -> N
CN -> C'''

sep = re.compile(r'\n^$\n', flags=re.MULTILINE)

def parse(string):
    start, inserts = sep.split(string)
    inserts = dict(rule.split(' -> ') for rule in inserts.splitlines())
    return (start, inserts)

def step(start, rules):
    string_list = list(start)
    new = [string_list[0]]
    for a, b in zip(string_list[:-1], string_list[1:]):
        if a+b in rules:
            new.append(rules[a+b])
        new.append(b)
    return ''.join(new)

def step_deque(string_deque, rules):
    i1 = iter(string_deque)
    i2 = iter(string_deque)
    # load new with first element
    new = deque([next(i1)])
    # offset second pair
    next(i2)
    next(i2)
    for a, b in zip(i1, i2):
        try:
            new.append(rules[a+b])
        except KeyError:
            pass
        new.append(b)
    return new

def steps(start, inserts, nsteps):
    string_deque = deque(start)
    for _ in range(nsteps):
        string_deque = step_deque(string_deque, inserts)
    string_deque = list(string_deque)

def calcspread(polymer):
    counts = Counter(polymer)
    least = min(counts, key=lambda key: counts[key])
    most = max(counts, key=lambda key: counts[key])
    spread = counts[most] - counts[least]
    return spread

def example1():
    expects = [
        'NCNBCHB',
        'NBCCNBBBCBHCB',
        'NBBBCNCCNBBNBNBBCHBHHBCHB',
        'NBBNBNBBCCNBCNCCNBBNBBNBBBNBBNBBCBHCBHHNHCBBCBHCB',
    ]
    string, inserts = parse(_day14_example)
    start = string
    # XXX
    # LEFT OFF HERE
    # Much too slow with lists and strings ~14 minutes.
    for index in range(len(expects)):
        string = step(string, inserts)
        expect = expects[index]
        assert string == expect, f'{new=} != {expect=}'
    return
    #
    polymer = steps(start, inserts, 10)
    spread = calcspread(polymer)
    assert spread == 1588, f'{spread=} != 1588'

def day14_part1():
    """
    Day 14 Part 1
    """
    example1()
    string, rules = parse(readinput(14))
    spread = steps(string, rules, 10)
    print(f'Day 14 Part 1 Solution: {spread=}')

def example2():
    string, inserts = parse(_day14_example)
    spread = steps(string, inserts, 40)
    assert spread == 2188189693529, f'{spread=} != 2188189693529'

def day14_part2():
    example2()
