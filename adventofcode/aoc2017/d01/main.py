import os

def summatching(digits, steps=1):
    n = len(digits)
    return sum(int(d) for i, d in enumerate(digits) if d == digits[(i + steps) % n])

def tests():
    assert summatching("1122") == 3
    assert summatching("1111") == 4
    assert summatching("1234") == 0
    assert summatching("91212129") == 9

    assert summatching("1212", 2) == 6
    assert summatching("1221", 2) == 0
    assert summatching("123425", 3) == 4
    assert summatching("123123", 3) == 12
    assert summatching("12131415", 4) == 4

def main():
    tests()

    # 1167 too low
    path = os.path.join(os.path.dirname(__file__), "input.txt")
    input_ = open(path).read().strip()
    print("part 1 answer: %s" % summatching(input_))

    print("part 2 answer: %s" % summatching(input_, int(len(input_)/2)))

if __name__ == "__main__":
    main()
