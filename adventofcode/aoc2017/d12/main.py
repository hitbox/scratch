import os

TEST = """\
0 <-> 2
1 <-> 1
2 <-> 0, 3, 4
3 <-> 2, 4
4 <-> 2, 3, 6
5 <-> 6
6 <-> 5, 4"""

class Comms:

    def __init__(self, inputstr):
        self.state = self.parse(inputstr)

    def parse(self, s):
        state = {}
        for line in s.splitlines():
            left, right = line.split(" <-> ")
            state[left] = right.split(", ")
        return state

    def can_talk(self, program, target, seen=None):
        """
        Can `program` talk to `target`?
        """
        if seen is None:
            seen = []
        comm = self.state[program]
        if target in comm:
            return True
        else:
            for sub in comm:
                if sub in seen:
                    continue
                seen.append(sub)
                if self.can_talk(sub, target, seen):
                    return True
        return False

    def iter_can_talk(self, target):
        for program in self.state:
            if self.can_talk(program, target):
                yield program

    def count_can_talk(self, target):
        return count(self.iter_can_talk(target))

    def groups(self):
        grouped = list()
        seen = set()
        for n, p1 in enumerate(self.state, start=1):
            complete = (n / len(self.state)) * 100
            if complete % 1 == 0:
                print("complete: %s%%" % (complete, ))
            if p1 in seen:
                continue
            seen.add(p1)
            group = set([p1])
            for p2 in self.iter_can_talk(p1):
                if p2 != p1 and p2 in seen:
                    break
                group.add(p2)
                seen.add(p2)
            else:
                if group not in grouped:
                    grouped.append(group)
        return grouped


def count(iterable):
    n = 0
    for whatever in iterable:
        n += 1
    return n

def tests():
    comms = Comms(TEST)
    assert comms.count_can_talk("0") == 6

    print(comms.groups())
    assert len(comms.groups()) == 2

def get_input():
    return open(os.path.join(os.path.dirname(__file__), "input.txt")).read().strip()

def main():
    tests()

    comms = Comms(get_input())
    print("part 1: %s" % (comms.count_can_talk("0")))
    print("part 2: %s" % (len(comms.groups())))
    # part 2: 179 after several minutes

    # tried aborting the inner-loop of `groups`, didn't speed up much

if __name__ == "__main__":
    main()
