#!python
import os

paren2num = { '(': 1, ')': -1 }

def parse(s):
    return (paren2num[c] for c in s)

def getinput():
    return open(os.path.join('inputs', 'day01.input')).read()

def part1():
    data = parse(getinput())
    print sum(data)

def part2():
    data = parse(getinput())

    s = 0
    for i, n in enumerate(data, start=1):
        s += n
        if s < 0:
            break

    print 'Position of character that causes Santa to enter basement: %s' % (i, )

if __name__ == '__main__':
    part1()
    part2()
