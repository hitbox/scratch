#!python
import re
from pprint import pprint as pp
from adventlib import input_path

class Reindeer(object):

    def __init__(self, name, rate, flytime, resttime):
        self.name = name
        self.rate = rate
        self.flytime = flytime
        self.resttime = resttime

        self.state = 'fly'
        self.runtime = flytime

        self.distance = 0
        self.points = 0

    def update(self):
        self.runtime -= 1

        if self.state == 'fly':
            self.distance += self.rate

        if self.runtime == 0:
            self.state = 'fly' if self.state == 'rest' else 'rest'
            self.runtime = self.flytime if self.state == 'fly' else self.resttime


def parse(text):
    _re = re.compile('(?P<name>[A-Z][a-z]+) can fly (?P<rate>\d+) km/s'
                     ' for (?P<flytime>\d+) seconds, but then must rest '
                     'for (?P<resttime>\d+) seconds\.').match
    r = []
    for line in text.splitlines():
        m = _re(line)
        if m is None:
            continue
        attrs = m.groupdict()
        for k in ['rate', 'flytime', 'resttime']:
            attrs[k] = int(attrs[k])
        r.append(attrs)
    return r

def points(reindeers):
    farthest = max(deer.distance for deer in reindeers)
    for deer in reindeers:
        if deer.distance == farthest:
            deer.points += 1

def test():
    comet = Reindeer('Comet', 14, 10, 127)
    dancer = Reindeer('Dancer', 16, 11, 162)

    for _ in range(1000):
        comet.update()
        dancer.update()
        points([comet, dancer])

    assert comet.distance == 1120
    assert dancer.distance == 1056

    assert comet.points == 312
    assert dancer.points == 689

def main():
    data = open(input_path(__file__, 1)).read()

    reindeers = [ Reindeer(attrs['name'], attrs['rate'], attrs['flytime'], attrs['resttime'])
                  for attrs in parse(data) ]

    for _ in range(2503):
        for deer in reindeers:
            deer.update()
        points(reindeers)

    print 'Part 1: %s' % (max(d.distance for d in reindeers), )

    print 'Part 2: %s' % (max(d.points for d in reindeers), )

if __name__ == '__main__':
    test()
    main()
