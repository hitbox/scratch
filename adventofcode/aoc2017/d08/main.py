import collections
import operator
import os
import re
import textwrap

char2op = {"<": operator.lt, ">": operator.gt, "<=": operator.le,
           ">=": operator.ge, "==": operator.eq, "!=": operator.ne}

def parser(inputstr):
    registers = collections.defaultdict(int)
    instruction_re = re.compile("([a-z]+) (inc|dec) (\-?[0-9]+) if ([a-z]+) ([<>=!]+) (\-?[0-9]+)")
    for line in inputstr.splitlines():
        m = instruction_re.match(line)
        register, op, value, condregister, condition, condvalue = m.groups()

        op = operator.add if op == "inc" else operator.sub
        value = int(value)
        condition = char2op[condition]
        condvalue = int(condvalue)

        if condition(registers[condregister], condvalue):
            registers[register] = op(registers[register], value)

        yield registers

def consume(iterable):
    for whatever in iterable:
        pass
    return whatever

def find_highest(inputstr):
    highest = None
    for state in parser(inputstr):
        largest = max(state.values())
        if highest is None or largest > highest:
            highest = largest
    return highest

def tests():
    inputstr = "".join(textwrap.dedent("""\
        b inc 5 if a > 1
        a inc 1 if b < 5
        c dec -10 if a >= 1
        c inc -20 if c == 10"""))
    assert max(consume(parser(inputstr)).values()) == 1
    assert find_highest(inputstr) == 10

def main():
    tests()

    inputstr = open(os.path.join(os.path.dirname(__file__), "input.txt")).read()

    registers = consume(parser(inputstr))
    largest = max(registers.values())
    print("part 1: %s" % (largest, ))

    print("part 2: %s" % (find_highest(inputstr), ))

if __name__ == "__main__":
    main()
