from common import puzzle, isint

class Program(object):

    def __init__(self, a=0, b=0, c=0, d=0):
        self.a, self.b, self.c, self.d = a, b, c, d
        self.current = 0

    def __str__(self):
        return 'a: %s, b: %s, c: %s, d: %s' % (self.a, self.b, self.c, self.d)

    def run(self, code, debug=False):
        lines = [line.split() for line in code.splitlines()]

        while True:
            if self.current >= len(lines):
                break
            line = lines[self.current]
            if debug:
                print(self)
                print(' '.join(map(str, line)))
            command = line[0]

            if command == 'cpy':
                x, y = line[1:]
                if isint(x):
                    setattr(self, y, int(x))
                else:
                    setattr(self, y, getattr(self, x))
            elif command in ('inc', 'dec'):
                v = 1 if command == 'inc' else -1
                x = line[1]
                setattr(self, x, getattr(self, x) + v)
            elif command == 'jnz':
                x, y = line[1:]
                if (isint(x) and int(x) != 0) or getattr(self, x, None) != 0:
                    self.current += int(y)
                    continue
            self.current += 1


def tests():
    program = Program()
    code = """cpy 41 a
inc a
inc a
dec a
jnz a 2
dec a"""
    program.run(code, debug=True)
    assert program.a == 42

def part1():
    program = Program()
    program.run(puzzle(12).read())
    print('Part 1')
    print(program)

def part2():
    program = Program(c=1)
    program.run(puzzle(12).read())
    print('Part 2')
    print(program)

def main():
    tests()
    part1()
    part2()

if __name__ == '__main__':
    main()
