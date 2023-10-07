import collections
import os
import re
import textwrap

from pprint import pformat, pprint as pp

def oddity(iterable, key=None):
    if key is None:
        key = lambda x: x

    no_odd = (None, None)
    summary = collections.Counter(map(key, iterable))

    if len(summary) == 2:
        common, different = summary.items()
        if different[1] == common[1]:
            return no_odd

        if different[1] > common[1]:
            common, different = different, common
        rv = (common[0], different[0])
        return rv

    return no_odd

class Tower:

    def __init__(self):
        self.bottom = None
        self.tower = {}
        self.weights = {}

    def parse(self, inputstr):
        line_re = re.compile("(?P<name>[a-z]+) \((?P<weight>\d+)\)(?: \-> )?(?P<holding>.*)")
        for line in inputstr.splitlines():
            match = line_re.match(line)
            groups = match.groups()
            name, weight, holding = groups
            self.weights[name] = int(weight)
            if holding:
                holding = holding.split(", ")
                self.tower[name] = holding
        self.bottom = self._find_bottom()

    def _find_bottom(self):
        all_children = []
        for name, holding in self.tower.items():
            all_children.extend(holding)
        for name in self.tower:
            if name not in all_children:
                return name

    def _iter_weighted(self):
        totals = {}
        for name, _ in self.tower.items():
            if name == self.bottom:
                continue
            weight = self.weights[name]
            subweight = sum(w for p, w in self.get_program_weights(name))
            yield (name, weight, subweight)

    def get_program_weights(self, start=None):
        if start is None:
            start = self.bottom
        for holding in self.tower.get(start, ()):
            yield holding, self.weights[holding]
            if holding in self.tower:
                yield from self.get_program_weights(holding)

    def get_odd_program(self, program=None, goal=0):
        if program is None:
            program = self.bottom

        weights = {}
        for child in self.tower.get(program, ()):
            weights[child] = self.weights[child] + sum(w for p, w in self.get_program_weights(child))
        common, odd = oddity(weights.values())

        if odd:
            for child, weight in weights.items():
                if weight == odd:
                    return self.get_odd_program(child, common)
        else:
            # all children same, this program is the problem
            return program, sum(weights.values()), goal

    def solution(self):
        program, subweight, goal = self.get_odd_program()
        weight = self.weights[program]

        return weight + (goal - weight - subweight)

    def find_balanced_weight(self):
        totals = {}
        for name, weight, subweight in self._iter_weighted():
            total = weight + subweight
            if total not in totals:
                totals[total] = 0
            totals[total] += 1
        assert len(totals) == 2, pformat(totals)
        for total, count in totals.items():
            if count > 1:
                return total

    def find_corrected_weight(self):
        balanced_weight = self.find_balanced_weight()
        for name, weight, subweight in self._iter_weighted():
            holding = self.tower[name]
            total = weight + subweight

            if total != balanced_weight:
                correction = balanced_weight - weight - subweight
                return weight + correction

def tests():
    assert oddity("a") == (None, None)
    assert oddity("ab") == (None, None)
    assert oddity("baa") == ("a", "b")

    inputstr = "".join(textwrap.dedent("""\
                pbga (66)
                xhth (57)
                ebii (61)
                havc (66)
                ktlj (57)
                fwft (72) -> ktlj, cntj, xhth
                qoyq (66)
                padx (45) -> pbga, havc, qoyq
                tknk (41) -> ugml, padx, fwft
                jptl (61)
                ugml (68) -> gyxo, ebii, jptl
                gyxo (61)
                cntj (57)"""))
    tower = Tower()
    tower.parse(inputstr)
    assert tower.bottom == "tknk"
    assert tower.find_corrected_weight() == 60

    assert tower.solution() == 60

    # test with recursion
    inputstr = "".join(textwrap.dedent("""\
                pbga (66)
                xhth (57)
                ebii (61)
                havc (66)
                ktlj (57) -> qoyq
                fwft (72) -> ktlj, cntj, xhth
                qoyq (66) -> ebii
                padx (45) -> pbga, havc, qoyq
                tknk (41) -> ugml, padx, fwft
                jptl (61)
                ugml (68) -> gyxo, ebii, jptl
                gyxo (61)
                cntj (57)"""))
    # fwft (72) + [ktlj (57) + [qoyq (66) + ebii (61)]] + cntj (57) + xhth (57) == 370
    tower = Tower()
    tower.parse(inputstr)
    name = "fwft"
    assert tower.weights[name] + sum(w for p, w in tower.get_program_weights(name)) == 370

def main():
    tests()

    input_path = os.path.join(os.path.dirname(__file__), "input.txt")
    tower = Tower()
    tower.parse(open(input_path).read())

    print("part 1: %s" % tower.bottom)

    # 771 is too low
    # 960 is too low
    # 2300 is too high
    #
    #print("part 2: %s" % tower.find_corrected_weight())
    print("part 2: %s" % tower.solution())
    # Got fed up with this, cheated looking at Ned Batchelder's solution, still
    # had problems, his "My children are balanced, I'm the problem" helped me a
    # lot.
    # Leaving the code a mess.

if __name__ == "__main__":
    main()
