import os

def redistribute(banks):
    nbanks = len(banks)
    blocks = max(banks)
    choosen = banks.index(blocks)
    banks[choosen] = 0
    i = choosen
    for block in range(blocks):
        i = (i + 1) % nbanks
        banks[i] += 1

def find_cycle(banks):
    seen = set()
    steps = 0
    while True:
        redistribute(banks)
        steps += 1
        save = tuple(banks)
        if save in seen:
            break
        seen.add(save)
    return steps

def find_cycle2(banks):
    seen = set()
    first = {}
    steps = 0
    index = 0
    while True:
        redistribute(banks)
        steps += 1
        save = tuple(banks)
        if save in seen:
            break
        seen.add(save)
        first[save] = index
        index += 1
    return index - first[save]

def tests():
    assert find_cycle([0, 2, 7, 0]) == 5
    value, expected = find_cycle2([0, 2, 7, 0]), 4
    assert value == expected, "expected: %s, got: %s" % (expected, value)

def get_input():
    with open(os.path.join(os.path.dirname(__file__), "input.txt")) as f:
        return [int(char) for char in f.read().strip().split()]

def main():
    tests()
    print("part 1: %s" % (find_cycle(get_input())))
    print("part 2: %s" % (find_cycle2(get_input())))

if __name__ == "__main__":
    main()
