#!python
import re
import itertools
from pprint import pprint as pp
from adventlib import input_path

_parser_re = re.compile('(?P<origin>\S+) to (?P<destination>\S+) = (?P<distance>\d+)').match

def parseline(line):
    m = _parser_re(line)
    if m:
        d = m.groupdict()
        d['distance'] = int(d['distance'])
        return d
    raise RuntimeError('Invalid line %s' % (line, ))

def parseinput(lines):
    locations = set()
    distances = []
    for line in lines:
        line = line.strip()
        parsed = parseline(line)
        distances.append(parsed)
        locations.add(parsed['origin'])
        locations.add(parsed['destination'])
    return locations, distances

def distance(distlist, *locations):
    assert len(locations) == 2
    g = [d['distance'] for d in distlist if d['origin'] in locations and d['destination'] in locations]
    assert len(g) == 1
    d = g[0]
    return d

def sumdist(distlist, *locations):
    return sum([distance(distlist, a, b) for a,b in zip(locations[:-1], locations[1:])])

def test():
    inputstr = """London to Dublin = 464
                  London to Belfast = 518
                  Dublin to Belfast = 141"""

    locations, distances = parseinput(inputstr.splitlines())

    routes = itertools.permutations(locations)

    assert min(sumdist(distances, *t) for t in routes) == 605

    routes = itertools.permutations(locations)
    assert max(sumdist(distances, *t) for t in routes) == 982


def part1():
    inputstr = open(input_path(__file__, 1)).read()
    locations, distances = parseinput(inputstr.splitlines())

    routes = itertools.permutations(locations)
    print 'Part 1: distance of the shortest route: %s' % min(sumdist(distances, *t) for t in routes)

def part2():
    inputstr = open(input_path(__file__, 1)).read()
    locations, distances = parseinput(inputstr.splitlines())

    routes = itertools.permutations(locations)
    print 'Part 2: distance of the longest route: %s' % max(sumdist(distances, *t) for t in routes)

if __name__ == '__main__':
    test()
    part1()
    part2()
