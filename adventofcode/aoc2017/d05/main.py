import os

DEBUG = False

def part1_modifier(index, offset, state):
    state[index] += 1

def part2_modifier(index, offset, state):
    if offset > 2:
        state[index] += -1
    else:
        state[index] += 1

def find_exit(jumps, modifier=part1_modifier):
    steps = 0
    index = 0
    def print_state():
        print(' '.join('(%s)' % offset if i == index else '%3s' % offset
              for i, offset in enumerate(jumps)))
    if not DEBUG:
        print_state = lambda: None
    while True:
        try:
            offset = jumps[index]
        except IndexError:
            # found exit!
            break
        print_state()
        modifier(index, offset, jumps)
        index += offset
        steps += 1
    print_state()
    return steps

def tests():
    assert find_exit([0,3,0,1,-3]) == 5
    assert find_exit([0,3,0,1,-3], part2_modifier) == 10

def get_input():
    with open(os.path.join(os.path.dirname(__file__), "input.txt")) as f:
        return [int(line.strip()) for line in f.readlines()]

def main():
    tests()
    print("part 1: %s" % (find_exit(get_input())))
    print("part 2: %s" % (find_exit(get_input(), part2_modifier)))

if __name__ == "__main__":
    main()
