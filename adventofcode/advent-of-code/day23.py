#!python
from adventlib import input_path, safeint

DEBUG = False

class Computer(object):

    def __init__(self, a=0, b=0):
        self.current_index = 0
        self.registers = {'a': a, 'b': b}
        self.instructions = []

    def load(self, instructions):
        self.instructions = instructions

    def parse(self, text):
        instructions = []
        for line in text.splitlines():
            parts = line.split(' ')
            name = parts[0]
            args = tuple(( safeint(a.strip(',')) for a in parts[1:] ))
            instructions.append((name, args))
        return instructions

    def parse_and_load(self, text):
        self.load(self.parse(text))

    def execute(self, instruction, args):
        if DEBUG:
            print
            print 'current index: %s' % self.current_index
            print 'registers: %s' % self.registers
            print 'instruction: %s' % instruction
            print 'args: %s' % (args, )
            raw_input('enter to execute')
        func = getattr(self, instruction)
        func(*args)

    def next(self):
        self.current_index += 1

    def hlf(self, register):
        self.registers[register] /= 2
        self.next()

    def tpl(self, register):
        self.registers[register] *= 3
        self.next()

    def inc(self, register):
        self.registers[register] += 1
        self.next()

    def jmp(self, offset):
        self.current_index += offset

    def jie(self, register, offset):
        if self.registers[register] % 2 == 0:
            self.jmp(offset)
        else:
            self.next()

    def jio(self, register, offset):
        if self.registers[register] == 1:
            self.jmp(offset)
        else:
            self.next()

    def run(self):
        while True:
            if self.current_index > len(self.instructions) - 1:
                break
            instruction, args = self.instructions[self.current_index]
            self.execute(instruction, args)


def test1():
    program = """\
inc a
jio a, +2
tpl a
inc a"""
    computer = Computer()
    computer.parse_and_load(program)
    computer.run()
    assert computer.registers['a'] == 2

def part1():
    computer = Computer()
    computer.parse_and_load(open(input_path(__file__, 1)).read())
    computer.run()
    print 'Part 1: value of register b: %s' % (computer.registers['b'], )

def part2():
    computer = Computer(a=1)
    computer.parse_and_load(open(input_path(__file__, 1)).read())
    computer.run()
    print 'Part 2: value of register b: %s, starting with a = 1' % (computer.registers['b'], )

def main():
    test1()
    part1()
    part2()

if __name__ == '__main__':
    main()
