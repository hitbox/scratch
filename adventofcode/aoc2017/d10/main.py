import functools
import itertools
import operator
import os

class Knothash:

    def __init__(self, nelements, lengths):
        self.nelements = nelements
        self.lengths = lengths
        self.position = 0
        self.skip = 0
        self.circular = list(range(self.nelements))

    def dense_hash(self):
        return list(functools.reduce(operator.xor, block) for block in grouper(self.circular, 16))

    def final(self):
        return "".join(map(prettyhex, self.dense_hash()))

    def hash(self, nrounds=1):
        for _ in range(nrounds):
            for length in self.lengths:
                sublist = []
                i = self.position
                while len(sublist) < length:
                    sublist.append(self.circular[i])
                    i = (i + 1) % self.nelements
                sublist = reversed(sublist)

                i = self.position
                for value in sublist:
                    self.circular[i] = value
                    i = (i + 1) % self.nelements

                self.position = (self.position + length + self.skip) % self.nelements
                self.skip += 1

        return self.circular

def process_input(s):
    return [ord(c) for c in s] + [17, 31, 73, 47, 23]

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

def prettyhex(n):
    _, h = hex(n).split("0x")
    return "{:0>2}".format(h)

def tests():
    hasher = Knothash(5, [3,4,1,5])
    a, b = hasher.hash()[:2]
    assert a * b == 12

    assert process_input("1,2,3") == [49,44,50,44,51,17,31,73,47,23]

    assert list(grouper(range(10), 2)) == [(0,1),(2,3),(4,5),(6,7),(8,9)]

    assert prettyhex(64) == "40"
    assert prettyhex(7) == "07"
    assert prettyhex(255) == "ff"

    def test(inputstr, expected):
        hasher = Knothash(256, process_input(inputstr))
        hasher.hash(64)
        assert hasher.final() == expected

    test("", "a2582a3a0e66e6e86e3812dcb672a272")
    test("AoC 2017", "33efeb34ea91902bb2f59c9920caa6cd")
    test("1,2,3", "3efbe78a8d82f29979031a4aa0b16a9d")
    test("1,2,4", "63960835bcdc130f0b66d7ff4f6a5a8e")

def main():
    tests()

    inputstr = open(os.path.join(os.path.dirname(__file__), "input.txt")).read().strip()
    lengths = list(map(int, inputstr.split(",")))

    hasher = Knothash(256, lengths)
    a, b = hasher.hash()[:2]
    check = a * b
    print("part 1: %s" % (check, ))

    hasher = Knothash(256, process_input(inputstr))
    hasher.hash(64)
    print("part 2: %s" % (hasher.final(), ))

if __name__ == "__main__":
    main()
