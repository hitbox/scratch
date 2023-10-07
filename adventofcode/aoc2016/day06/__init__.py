import os

test1_data = """\
eedadn
drvtee
eandsr
raavrd
atevrs
tsrnev
sdttsa
rasrtv
nssdts
ntnada
svetve
tesnvt
vntsnd
vrdear
dvrsen
enarar"""

def countdict(chars):
    d = {}
    for c in chars:
        if not c in d:
            d[c] = 0
        d[c] += 1
    return d

def commonest(chars):
    d = countdict(chars)
    maxitem = max(d.items(), key=lambda item: item[1])
    return maxitem[0]

def rarest(chars):
    d = countdict(chars)
    leastitem = min(d.items(), key=lambda item: item[1])
    return leastitem[0]

def _recover(positions):
    listified = (list(position) for position in positions)
    rotated = zip(*listified)
    return rotated

def mostcommonrecover(positions):
    return ''.join(commonest(row) for row in _recover(positions))

def leastcommonrecover(positions):
    return ''.join(rarest(row) for row in _recover(positions))

def test1():
    assert mostcommonrecover(test1_data.splitlines()) == 'easter'

def test2():
    assert leastcommonrecover(test1_data.splitlines()) == 'advent'

def load():
    with open(os.path.join(os.path.dirname(__file__), 'input.txt')) as inputf:
        return (line.strip() for line in inputf.readlines())

def part1():
    print('Day 6, part 1: error-corrected message "%s"' % mostcommonrecover(load()))

def part2():
    print('Day 6, part 2: error-corrected message "%s"' % leastcommonrecover(load()))

def main():
    test1()
    part1()
    test2()
    part2()
