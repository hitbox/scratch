import os
from itertools import combinations

def rowchecksum(row):
    return max(row) - min(row)

def checksum(sheet):
    return sum(map(rowchecksum, sheet))

def is_evenly_divisible(a, b):
    return a % b == 0 or b % a == 0

def safe_div(a, b):
    return max((a,b)) / min((a,b))

def rowchecksum2(row):
    return sum((int(safe_div(a,b)) for a,b in combinations(row,2) if is_evenly_divisible(a,b)))

def checksum2(sheet):
    return sum(map(rowchecksum2, sheet))

def tests():
    # part 1
    assert rowchecksum((5,1,9,5)) == 8
    assert rowchecksum((7,5,3)) == 4
    assert rowchecksum((2,4,6,8)) == 6
    assert checksum(((5,1,9,5),(7,5,3),(2,4,6,8))) == 18
    # part 2
    assert rowchecksum2((5,9,2,8)) == 4
    assert rowchecksum2((9,4,7,3)) == 3
    assert rowchecksum2((3,8,6,5)) == 2
    assert checksum2(((5,9,2,8),(9,4,7,3),(3,8,6,5))) == 9

def row_reader(line):
    for value in line.split():
        yield int(value)

def input_reader(path):
    with open(path) as input_file:
        return [ list(map(int, line.split())) for line in input_file]

def main():
    tests()

    input_path = os.path.join(os.path.dirname(__file__), "input.txt")
    sheet = input_reader(input_path)
    print("part 1: %s" % checksum(sheet))
    print("part 2: %s" % checksum2(sheet))

if __name__ == "__main__":
    main()
