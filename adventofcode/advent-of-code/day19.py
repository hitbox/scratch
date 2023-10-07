#!python2
from copy import deepcopy
from pprint import pprint as pp

from adventlib import input_path, parseargs2

# SECOND ATTEMPT AT PART 2 GAVE UP
# see day19cheat.py

SIMPLE_MACHINE = """\
H => HO
H => OH
O => HH
HOH
"""

SIMPLE_MACHINE_2 = """\
e => H
e => O
H => HO
H => OH
O => HH
HOH
"""

TEST_MACHINE = """\
Hi => HO
Hi => OH
H => B
Oi => HH
HiOH
"""

# the whole input machine with simpler start
SIMPLIFIED = """\
Al  =>  ThF
Al  =>  ThRnFAr
B   =>  BCa
B   =>  TiB
B   =>  TiRnFAr
Ca  =>  CaCa
Ca  =>  PB
Ca  =>  PRnFAr
Ca  =>  SiRnFYFAr
Ca  =>  SiRnMgAr
Ca  =>  SiTh
F   =>  CaF
F   =>  PMg
F   =>  SiAl
H   =>  CRnAlAr
H   =>  CRnFYFYFAr
H   =>  CRnFYMgAr
H   =>  CRnMgYFAr
H   =>  HCa
H   =>  NRnFYFAr
H   =>  NRnMgAr
H   =>  NTh
H   =>  OB
H   =>  ORnFAr
Mg  =>  BF
Mg  =>  TiMg
N   =>  CRnFAr
N   =>  HSi
O   =>  CRnFYFAr
O   =>  CRnMgAr
O   =>  HP
O   =>  NRnFAr
O   =>  OTi
P   =>  CaP
P   =>  PTi
P   =>  SiRnFAr
Si  =>  CaSi
Th  =>  ThCa
Ti  =>  BP
Ti  =>  TiTi
e   =>  HF
e   =>  NAl
e   =>  OMg

CRnFYFYFArPMg
"""

def pindent(depth, s, *fmtargs):
    indent = '  ' * depth
    print indent + s % fmtargs

class Machine(object):

    def __init__(self, machine_text):
        self.machine_text = machine_text
        self.machine = None
        self.start = None
        self._needles = None

    def get_machine_and_start(self, s):
        machine = {}
        start = None
        for line in s.splitlines():
            if not line:
                continue
            left_and_right = line.split(' => ')
            if len(left_and_right) > 1:
                left, right = left_and_right
                left = left.strip()
                right = right.strip()
                if left in machine:
                    machine[left].append(right)
                else:
                    machine[left] = [right]
            else:
                start = left_and_right[0]
                break
        else:
            raise RuntimeError('Failed to parse machine string.')
        return machine, start

    def get_reducer_and_start(self, s):
        machine, start = self.get_machine_and_start(s)

        reducer = {}
        for key, values in machine.iteritems():
            for value in values:
                reducer[value] = key

        return reducer, start

    def init(self):
        self.machine, self.start = self.get_reducer_and_start(self.machine_text)
        self._needles = None

    def find(self, target):
        self.init()

        # prevent target from being replaced
        self.machine = { key:value for key, value in self.machine.items() if key != target }

        #pp(self.machine)
        #print

        return self.reduce(target, self.start)

    def get_needles(self):
        if self._needles is None:
            self._needles = sorted(self.machine.keys(), key=len, reverse=True)
        return self._needles

    def get_replacements(self, current):
        for needle in self.get_needles():
            #print 'needle: %r' % needle
            if needle not in current:
                continue
            replacement = self.machine[needle]
            #print 'replacement: %r' % replacement
            yield (needle, replacement)

    def reduce(self, target, path_or_start, depth=0):
        if path_or_start is None:
            yield
            return

        #pindent(depth, 'path_or_start: %r', path_or_start)

        if isinstance(path_or_start, basestring):
            path = [path_or_start]
        else:
            path = path_or_start

        current = path[-1]

        #pindent(depth, 'path: %r, current: %r', path, current)

        if current == target:
            #pindent(depth, 'found: %r == %r', current, target)
            yield path
            return
        elif target in current:
            #pindent(depth, 'nope')
            yield
            return

        depth += 1
        for needle, replacement in self.get_replacements(current):
            if needle not in current:
                continue
            #pindent(depth, 'needle: %r, replacement: %r', needle, replacement)

            replaced = current.replace(needle, replacement)

            pathgenerator = self.reduce(target, path+[replaced], depth+1)
            for anotherpath in pathgenerator:
                if anotherpath:
                    yield anotherpath


def simplified():
    text = SIMPLIFIED
    machine = Machine(text)

    for path in machine.find('e'):
        print path

def part2():
    text = open(input_path(__file__, 1)).read()
    machine = Machine(text)

    for path in machine.find('e'):
        print path


def main():
    args = parseargs2(other='simplified')
    if args.command == 'part2':
        part2()
    elif args.command == 'simplified':
        simplified()

if __name__ == '__main__':
    main()
