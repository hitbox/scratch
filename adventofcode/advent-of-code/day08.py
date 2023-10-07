#!python
from pprint import pprint as pp
from adventlib import input_path

def memorystring(line):
    return line.decode('string-escape')

def counts1(line):
    """
    return (code_count, memory_count)
    """
    # assumes wrapped in quotes
    return len(line), len(memorystring(line)) - 2

def counts2(line):
    return len(encode(line)), len(line)

def encode(s):
    return '"%s"' % ''.join('\\' + c if c in '"\\' else c for c in s)

def test():
    assert counts1(r'""') == (2, 0)
    assert counts1(r'"abc"') == (5, 3)
    assert counts1(r'"aaa\"aaa"') == (10, 7)
    assert counts1(r'"\x27"') == (6, 1)

    assert encode(r'""') == '"\\"\\""'
    assert encode(r'"abc"') == '"\\"abc\\""'
    assert encode(r'"aaa\"aaa"') == '"\\"aaa\\\\\\"aaa\\""'
    assert encode(r'"\x27"') == '"\\"\\\\x27\\""'

    assert counts2(r'""') == (6, 2)
    assert counts2(r'"abc"') == (9, 5)
    assert counts2(r'"aaa\"aaa"') == (16, 10)
    assert counts2(r'"\x27"') == (11, 6)

def total(lines, counter):
    code = 0
    mem = 0
    for line in lines:
        line = line.strip()
        c, m = counter(line)
        code += c
        mem += m
    return code, mem

def part1():
    text = open(input_path(__file__, 1)).read()
    code, mem = total(text.splitlines(), counts1)
    print 'Part 1: %s' % (code - mem)

def part2():
    text = open(input_path(__file__, 1)).read()
    code, mem = total(text.splitlines(), counts2)
    print 'Part 2: %s' % (code - mem)

if __name__ == '__main__':
    test()
    part1()
    part2()
