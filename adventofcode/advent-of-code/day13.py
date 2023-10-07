#!python
import re
import itertools
from pprint import pprint as pp
from adventlib import input_path

_process_re = re.compile('(?P<name1>[A-Z][a-z]+) would '
                         '(?P<op>(gain|lose)) (?P<amount>\d+) '
                         'happiness units by sitting next to '
                         '(?P<name2>[A-Z][a-z]+)\.').match

def parse(plantext):
    people = set()
    plan = {}
    for line in plantext.splitlines():
        m = _process_re(line)
        if m is not None:
            gd = m.groupdict()

            people.add(gd['name1'])
            people.add(gd['name2'])

            gd['amount'] = int(gd['amount'])
            gd['amount'] = -gd['amount'] if gd['op'] == 'lose' else gd['amount']

            key = (gd['name1'], gd['name2'])
            plan[key] = gd['amount']

    return (people, plan)

def happiness(plan, person, nextto):
    return plan[(person, nextto)]

def scoreplan(plan, seating):
    s = 0
    nseats = len(seating)
    r = 0
    for i, person in enumerate(seating):
        left = i - 1
        if left < 0:
            left = nseats - 1
        right = (i + 1) % nseats
        neighbors = [seating[left], seating[right]]
        score = sum(happiness(plan, person, neighbor) for neighbor in neighbors)
        r += score
    return r

def findhappiest(plan):
    people, plan = parse(plan)
    gen = ((seating, scoreplan(plan, seating))
           for seating in itertools.permutations(people))
    return max(gen, key=lambda x: x[1])

def tests():
    test_happiness = """\
Alice would gain 54 happiness units by sitting next to Bob.
Alice would lose 79 happiness units by sitting next to Carol.
Alice would lose 2 happiness units by sitting next to David.
Bob would gain 83 happiness units by sitting next to Alice.
Bob would lose 7 happiness units by sitting next to Carol.
Bob would lose 63 happiness units by sitting next to David.
Carol would lose 62 happiness units by sitting next to Alice.
Carol would gain 60 happiness units by sitting next to Bob.
Carol would gain 55 happiness units by sitting next to David.
David would gain 46 happiness units by sitting next to Alice.
David would lose 7 happiness units by sitting next to Bob.
David would gain 41 happiness units by sitting next to Carol."""

    happiest = findhappiest(test_happiness)
    assert happiest[1] == 330

def main():
    text = open(input_path(__file__, 1)).read()
    arrangement, total = findhappiest(text)
    print 'Part 1: arrangement: %s, total: %s' % (arrangement, total )

    #
    people, plan = parse(text)
    for person in people:
        text += 'Carl would gain 0 happiness units by sitting next to %s.\n' % person
        text += '%s would gain 0 happiness units by sitting next to Carl.\n' % person

    arrangement, total = findhappiest(text)
    print 'Part 2: arrangement: %s, total: %s' % (arrangement, total )

if __name__ == '__main__':
    tests()
    main()
