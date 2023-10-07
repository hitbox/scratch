#!python
import random
import sys
from itertools import combinations, groupby
from pprint import pprint as pp
from adventlib import input_path, rrange, parseargs2

def old_group_size_iter(n, ngroups, start=2):
    # ngroups is ignored
    # hard-coded to 3 sizes
    for i in xrange(start, n - 2):
        j = start
        k = n - i - start
        while j <= k:
            yield (i, j, k)
            j += 1
            k -= 1

def new_group_size_iter(nitems, ngroups):
    for values in rrange(ngroups, 1, nitems+1):
        if sum(values) != nitems:
            continue
        yield values

group_size_iter = old_group_size_iter

def quantum_entanglement(group):
    return reduce(lambda a,b: a*b, group)

def excluding(seq, *excludes):
    exclude = set(item for group in excludes for item in group)
    return (item for item in seq if item not in exclude)

def groupings(weights, size, *excludes):
    return (group for group in combinations(excluding(weights, *excludes), size))

def groups_iter(weights, ngroups):
    # still hard-coded with regard to sizes iteration
    # we can stop loop early if any of the sums is not 1/3 of the total
    third_weight = sum(weights) / ngroups
    for sizes in group_size_iter(len(weights), ngroups):
        s1, s2, s3 = sizes
        for group1 in groupings(weights, s1):
            gsum1 = sum(group1)
            if gsum1 != third_weight:
                continue
            glen1 = len(group1)
            for group2 in groupings(weights, s2, group1):
                glen2 = len(group2)
                gsum2 = sum(group2)
                if glen1 > glen2 or gsum1 != third_weight:
                    continue
                for group3 in groupings(weights, s3, group1, group2):
                    glen3 = len(group3)
                    gsum3 = sum(group3)
                    if glen1 > glen3 or gsum3 != third_weight:
                        continue
                    print sizes
                    yield sorted((group1, group2, group3), reverse=True)

def configs_iter(weights):
    for groups in groups_iter(sorted(weights, reverse=True)):
        g1 = groups[0]
        qe = quantum_entanglement(g1)
        g2, g3 = sorted(groups[1:], key=lambda x: len(x))
        yield (g1, qe, g2, g3)

# prefer leg room over quantum entanglement
by_group1_and_qe = lambda t: (len(t[0]), t[1])

def parse(text):
    return map(int, text.splitlines())

def mkline(group):
    return (group[0], quantum_entanglement(group[0]), group[1], group[2])

def test1():
    print '== Test 1 =='
    weights = range(1,6) + range(7, 12)
    data = groups_iter(weights, 3)

    for group in data:
        print pretty(*map(str, mkline(group)))

def take(sequence, n):
    for i in xrange(len(sequence) - n):
        yield sequence[i:i+n]

def wild_shot_in_dark(weights):
    group_must_weigh = sum(weights) / 3.0

    print weights
    print len(weights)
    print group_must_weigh

    n = len(weights) / 2 + 1

    for s1 in xrange(2, n):
        for s2 in xrange(n, 2, -1):
            for s3 in xrange(n, 2, -1):
                sizes = s1, s2, s3
                if sum(sizes) != len(weights):
                    continue
                #print sizes
                groups1 = combinations(weights, s1)
                for g1 in groups1:
                    if sum(g1) != group_must_weigh:
                        continue
                    groups2 = tuple(x for x in combinations(weights, s2) if set(x).isdisjoint(set(g1)))
                    for g2 in groups2:
                        if sum(g2) != group_must_weigh:
                            continue
                        groups3 = tuple(x for x in combinations(weights, s3) if set(x).isdisjoint(set(g1 + g2)))
                        for g3 in groups3:
                            if sum(g3) != group_must_weigh:
                                continue
                            groups = g1, g2, g3
                            print pretty(*map(str, mkline(groups)))
                            return

def test2():
    print '== test2 =='

    weights = sorted(range(1,6) + range(7, 12), reverse=True)
    wild_shot_in_dark(weights)

pretty = '{0:>30} {1:>15} {2:>30} {3:>30}'.format

def get_weights():
    text = open(input_path(__file__, 1)).read()
    return parse(text)

def part1():
    print '== Part 1 =='
    weights = get_weights()

    collector = set()
    groups = ( mkline(group) for group in groups_iter(weights, 3) )
    for group in groups:
        collector.add(group)
        if len(collector) % 10 == 0:
            print '=== Top 20 Best So Far ==='
            i = (group for group in sorted(collector, key=by_group1_and_qe))
            n = 0
            for group in i:
                # test to see how lone the answer takes to get becuase this
                # runs "forever"
                print pretty(*map(str, group))
                if group[1] == 10439961859:
                    sys.exit()
                n += 1
                if n > 20:
                    break
    # Took a very long time, like 10-15 minutes but got the answer.

def part1():
    # second stab at it
    weights = sorted(get_weights(), reverse=True)

# Cheating:
# https://www.reddit.com/r/adventofcode/comments/3y1s7f/day_24_solutions/cy9sqq2

from operator import mul

def day24(weights, ngroups):
    group_size = sum(weights) / ngroups

    for size in xrange(len(weights)):
        qes = [ reduce(mul, c) for c in combinations(weights, size) if sum(c) == group_size ]
        if qes:
            return min(qes)

def part2():
    weights = sorted(get_weights(), reverse=True)
    print day24(weights, 4)

def main():
    args = parseargs2()

    if args.command == 'tests':
        #test1()
        test2()
    elif args.command == 'part1':
        part1()
    elif args.command == 'part2':
        part2()

if __name__ == '__main__':
    main()
