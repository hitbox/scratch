import functools
import math

quarterturn = math.tau / 4

@functools.lru_cache(None)
def cos(angle):
    return int(math.cos(angle))

@functools.lru_cache(None)
def sin(angle):
    return int(math.sin(angle))

class Spiralxy:

    def __init__(self, limit):
        self.limit = limit
        self.space = set()
        self.values = {}
        self.angle = math.radians(270)
        self.square = 1
        self.x, self.y = 0, 0

    def __iter__(self):
        return self

    def __next__(self):
        if not self.space:
            self.space = set([(self.x, self.y)])
            self.values[(self.x, self.y)] = self.square
            self.square += 1
            return ((self.x, self.y), self.space)

        if self.limit == 1:
            raise StopIteration

        if self.square <= self.limit:
            turn = self.angle + quarterturn
            dx, dy = cos(turn), sin(turn)
            if (self.x + dx, self.y + dy) not in self.space:
                self.angle = turn
            else:
                dx, dy = cos(self.angle), sin(self.angle)
            self.x += dx
            self.y += dy
            self.space.add((self.x, self.y))
            self.values[(self.x, self.y)] = sum(self.values.get((self.x + dx, self.y + dy), 0)
                                                for dx, dy
                                                in ((1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)))
            self.square += 1
            return ((self.x, self.y), self.space)

        raise StopIteration

def adjacent(n):
    spiralxy = Spiralxy(n)
    for pos, space in spiralxy:
        pass
    return spiralxy.values[pos]

def position(n):
    spiralxy = Spiralxy(n)
    for pos, space in spiralxy:
        pass
    return pos

def get_steps(pos, dest=(0,0)):
    x, y = pos
    steps = 0
    while True:
        if x == dest[0] and y == dest[1]:
            break
        if x < dest[0]:
            x += 1
            steps += 1
        elif x > dest[0]:
            x -= 1
            steps += 1
        if y < dest[1]:
            y += 1
            steps += 1
        elif y > dest[1]:
            y -= 1
            steps += 1
    return steps

def tests():
    # part 1
    expects = { 1: (0,0),
                2: (1,0),
                3: (1,1),
                4: (0,1),
                5: (-1,1),
                6: (-1,0),
                7: (-1,-1),
                8: (0,-1),
                9: (1,-1),
                10: (2,-1),
                11: (2,0),
                12: (2,1),
                13: (2,2),
                14: (1,2),
                15: (0,2),
                16: (-1,2),
                17: (-2,2),
                18: (-2,1),
                19: (-2,0),
                20: (-2,-1),
                21: (-2,-2),
                22: (-1,-2),
                23: (0,-2),
            }

    for n, expected in expects.items():
        pos = position(n)
        assert pos == expected, "n: %s, pos: %s, expected: %s" % (n, pos, expected)

    assert get_steps(position(1)) == 0
    assert get_steps(position(12)) == 3
    assert get_steps(position(23)) == 2
    assert get_steps(position(1024)) == 31

    # part 2
    assert adjacent(1) == 1
    assert adjacent(2) == 1
    assert adjacent(3) == 2
    assert adjacent(4) == 4
    assert adjacent(5) == 5
    assert adjacent(6) == 10
    assert adjacent(7) == 11
    assert adjacent(8) == 23
    assert adjacent(9) == 25
    assert adjacent(10) == 26
    assert adjacent(11) == 54
    assert adjacent(12) == 57
    assert adjacent(13) == 59
    assert adjacent(14) == 122
    assert adjacent(15) == 133
    assert adjacent(16) == 142
    assert adjacent(17) == 147
    assert adjacent(18) == 304
    assert adjacent(19) == 330
    assert adjacent(20) == 351
    assert adjacent(21) == 362
    assert adjacent(22) == 747
    assert adjacent(23) == 806

def main():
    tests()
    inputvalue = 289326
    print("part 1: %s" % (get_steps(position(inputvalue)), ))

    spiralxy = Spiralxy(inputvalue)
    for pos, space in spiralxy:
        if spiralxy.values[pos] > inputvalue:
            print("part 2: %s" % (spiralxy.values[pos]))
            break

if __name__ == "__main__":
    main()
