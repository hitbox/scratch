#!python
import os
import re
from itertools import izip_longest
from pprint import pprint as pp
from collections import defaultdict
from adventlib import input_path

TICKER = {
    'children': 3,
    'cats': 7,
    'samoyeds': 2,
    'pomeranians': 3,
    'akitas': 0,
    'vizslas': 0,
    'goldfish': 5,
    'trees': 3,
    'cars': 2,
    'perfumes': 1,
}

class LineParser(object):

    pattern = 'Sue (?P<sue>\d+): (?P<attrs>.*)'

    def __init__(self):
        self._re = re.compile(self.pattern).match

    def __call__(self, line):
        match = self._re(line)
        if match:
            suedict = match.groupdict()
            suedict['sue'] = int(suedict['sue'])
            marshal = lambda k, v: (k, int(v))
            suedict['attrs'] = dict(marshal(*item.split(': '))
                                    for item in suedict['attrs'].split(', '))
            return suedict


def parse(text):
    parser = LineParser()

    sues = []
    for line in text.splitlines():
        sues.append(parser(line))
    return sues

def get_matches(sue, matcher):
    matches = {}
    for tickerkey, tickervalue in TICKER.items():
        if matcher(tickerkey, tickervalue, sue):
            matches[tickerkey] = tickervalue
    return matches

def part1_matcher(tickerkey, tickervalue, sue):
    return tickerkey in sue['attrs'] and tickervalue == sue['attrs'][tickerkey]

def part2_matcher(tickerkey, tickervalue, sue):
    if tickerkey in ('cats', 'trees'):
        return tickerkey in sue['attrs'] and tickervalue <= sue['attrs'][tickerkey]
    if tickerkey in ('pomeranians', 'goldfish'):
        return tickerkey in sue['attrs'] and tickervalue >= sue['attrs'][tickerkey]
    return part1_matcher(tickerkey, tickervalue, sue)

def find_sue(sues_data, matcher):
    suematches = {}
    for sue_data in sues_data:
        matches = get_matches(sue_data, matcher)
        if matches:
            suematches[sue_data['sue']] = matches
    return sorted(suematches.items(), key=lambda sueitem: len(sueitem[1]))[-1]

def main():
    sues_data = parse(open(input_path(__file__, 1)).read())
    print 'Part 1: The Sue: %s' % (find_sue(sues_data, part1_matcher), )
    print 'Part 2: The Sue: %s' % (find_sue(sues_data, part2_matcher), )

if __name__ == '__main__':
    main()
