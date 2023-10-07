import os

TEST = """\
0: 3
1: 2
4: 4
6: 4"""

TOP = 0

def parse(inputstr):
    layers = []
    for line in inputstr.splitlines():
        depth, range_ = map(int, line.split(": "))
        while len(layers) < depth:
            layers.append(0)
        layers.append(range_)
    return layers

def scanner_position(range_, second):
    amplitude = range_ - 1
    return abs(((second + amplitude) % (amplitude * 2)) - amplitude)

def severity(layers):
    damage = 0
    for second in range(len(layers)):
        range_ = layers[second]
        if range_ > 0:
            sp = scanner_position(range_, second)
            hit = sp == TOP
            if hit:
                depth = second
                damage += depth * range_
    return damage

def fewest_delays(layers):
    delay = 0
    nlayers = len(layers)
    while True:
        packet = 0
        second = delay
        while True:
            range_ = layers[packet]
            sp = scanner_position(range_, second)
            if range_ > 0 and sp == TOP:
                break
            packet += 1
            second += 1
            if packet == nlayers:
                return delay
        delay += 1

def tests():
    layers = parse(TEST)
    assert severity(layers) == 24
    assert fewest_delays(layers) == 10

def get_input():
    return open(os.path.join(os.path.dirname(__file__), "input.txt")).read().strip()

def main():
    tests()

    layers = parse(get_input())
    solution = severity(layers)
    assert solution == 1476
    print("part 1: %s" % (solution, ))

    solution = fewest_delays(layers)
    assert solution == 3937334
    print("part 2: %s" % (solution, ))

if __name__ == "__main__":
    main()
