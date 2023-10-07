#!python2
from pprint import pprint as pp
from adventlib import input_path, safeint

class AND(object):
    def __call__(self, x, y):
        return x & y


class OR(object):
    def __call__(self, x, y):
        return x | y


class LSHIFT(object):
    def __call__(self, x, y):
        return x << y


class RSHIFT(object):
    def __call__(self, x, y):
        return x >> y


class NOT(object):
    def __call__(self, x):
        return ~x & 65535


OPS = {
    'AND': AND,
    'OR': OR,
    'LSHIFT': LSHIFT,
    'RSHIFT': RSHIFT,
    'NOT': NOT,
}
OPS_VALUES = tuple(OPS.values())

def makecircuit(text):
    circuit = {}
    for line in text.splitlines():
        line = line.strip()
        lhs, endpoint = line.split(' -> ')
        result = get_op(lhs)
        if result:
            name, op = result
            i1, i2 = map(str.strip, lhs.split(name))
            args = tuple(safeint(i) for i in [i1, i2] if i)
            circuit[op] = args
            circuit[endpoint] = op
        else:
            circuit[endpoint] = safeint(lhs)
    return circuit

def get_op(s):
    for k,v in OPS.items():
        if k in s:
            return k,v()

def isop(thing):
    return isinstance(thing, OPS_VALUES)

def isint(thing):
    r = isinstance(thing, int)
    return r

def is_sequence(thing):
    try:
        iter(thing)
    except ValueError:
        return False
    else:
        return True

def resolve(circuit, key):
    if isop(key):
        op = key
        args = [ resolve(circuit, value) for value in circuit[key] ]
        r = op(*args)
        return r

    elif isint(key):
        return key

    else:
        r = resolve(circuit, circuit[key])
        circuit[key] = r
        return r

def tests():
    known_circuit = """\
    123 -> x
    456 -> y
    x AND y -> d
    x OR y -> e
    x LSHIFT 2 -> f
    y RSHIFT 2 -> g
    NOT x -> h
    NOT y -> i"""

    circuit = makecircuit(known_circuit)
    known_good = { 'd': 72, 'e': 507, 'f': 492, 'g': 114, 'h': 65412,
                   'i': 65079, 'x': 123, 'y': 456 }
    for k in 'defghi':
        r = resolve(circuit, k)
        assert known_good[k] == r

def part1():
    text = open(input_path(__file__, 1)).read()
    circuit = makecircuit(text)
    answer = resolve(circuit, 'a')
    print 'Part 1: circuit a: %s' % (answer, )
    return answer

def part2(a):
    # Now, take the signal you got on wire a, override wire b to that signal,
    # and reset the other wires (including wire a). What new signal is
    # ultimately provided to wire a?
    text = open(input_path(__file__, 1)).read()
    circuit = makecircuit(text)
    circuit['b'] = a
    print 'Part 2: circuit a: %s' % (resolve(circuit, 'a'), )

def main():
    tests()
    a = part1()
    part2(a)

if __name__ == '__main__':
    main()
