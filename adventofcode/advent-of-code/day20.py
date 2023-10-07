#!python
import argparse
from pprint import pprint as pp
from adventlib import parseargs

def deliver(nhouses, whilefunc):
    houses = { i: 0 for i in range(1, nhouses) }

    for house in range(1, nhouses):
        for elf in range(1, nhouses):
            if house % elf == 0:
                present = elf * 10
                houses[house] += present
                if not whilefunc(houses):
                    return houses

    return houses

def visited_by(house):
    yield 1
    if house > 1:
        yield house
        for elf in xrange(2, house):
            if elf > house / 2.0:
                return
            if house % elf == 0:
                yield elf

def presents(house, perhouse):
    return sum( elf * perhouse for elf in factors(house) )

def factors(n):
    # aka: elves
    if n == 1:
        yield 1
        return
    for i in xrange(1, n + 1):
        x, r = divmod(n, i)
        if r == 0 and i <= x:
            yield i
            if x != i:
                yield x
        if i >= x:
            return

def first_50(house):
    for elf1 in xrange(1, house + 1):
        elf2, remainder = divmod(house, elf1)

        if remainder == 0:
            if house <= elf1 * 50:
                yield elf1
            if elf1 != elf2 and house <= elf2 * 50:
                yield elf2

        if elf1 >= elf2:
            break

def tests():
    assert presents(1, 10) == 10
    assert presents(2, 10) == 30
    assert presents(3, 10) == 40
    assert presents(4, 10) == 70
    assert presents(5, 10) == 60
    assert presents(6, 10) == 120
    assert presents(7, 10) == 80
    assert presents(8, 10) == 150
    assert presents(9, 10) == 130

def get_start(target, perhouse):
    step = 100000
    house = 1
    row = 0
    while True:
        if presents(house, perhouse) >= target:
            row += 1
            if abs(step) == 1:
                break
            step /= -2
        house += step
    return house

def part1():
    target = 33100000

    #target /= 10

    house = get_start(target, 10)

    houses = []
    for house in xrange(house, 0, -1):
        p = presents(house, 10)
        if p >= target:
            houses.append(house)

    # 2016-05-19
    # Brute force output:
    # 2278236
    # 776160 <--
    #
    # real    9m2.107s
    # user    0m0.000s
    # sys     0m0.031s
    # And that is the answer!

def part2():
    target = 33100000

    for house in xrange(1000, target):
        x = sum(elf * 11 for elf in first_50(house))
        if house % 100 == 0:
            print 'house: %s, presents: %s' % (house, x)
        if x >= target:
            break

    print 'Part 2: %s' % (house, )

    # someone else's guess: 831600

def main():
    args = parseargs(requirepart=True)
    tests()
    if args.part == 1:
        part1()
    elif args.part == 2:
        part2()

if __name__ == '__main__':
    main()
