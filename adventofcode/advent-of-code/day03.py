#!python
import os

DIRMAP = { '<': (-1, 0), '>': (1, 0), '^': (0, -1), 'v': (0, 1) }

class Santa(object):
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.houses = { self.house: 1 }

    @property
    def house(self):
        return (self.x, self.y)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def down_chimney(self):
        if self.house in self.houses:
            self.houses[self.house] += 1
        else:
            self.houses[self.house] = 1

    def goto(self, house):
        dx, dy = house
        self.move(dx, dy)
        self.down_chimney()

    def run(self, directions):
        for house in directions:
            self.goto(house)
        return self

def parse(text):
    return (DIRMAP[c] for c in text)

def tests():
    assert len(Santa().run(parse('>')).houses) == 2
    assert len(Santa().run(parse('^>v<')).houses) == 4
    assert len(Santa().run(parse('^v^v^v^v^v')).houses) == 2

    assert len(unique_houses(*nsantas(parse('^v')))) == 3
    assert len(unique_houses(*nsantas(parse('^>v<')))) == 3
    assert len(unique_houses(*nsantas(parse('^v^v^v^v^v')))) == 11

def part1():
    text = open(os.path.join('inputs', 'day03.input')).read()
    instructions = parse(text)
    santa = Santa()
    santa.run(instructions)

    print '%s houses get at leat one present' % (len(santa.houses), )

def nsantas(instructions, n=2):
    santas = [ Santa() for _ in range(n) ]
    running = True
    while running:
        for santa in santas:
            move = next(instructions, None)
            if move is None:
                running = False
                break
            santa.move(*move)
            santa.down_chimney()
    return santas

def unique_houses(*santas):
    houses = set()
    for santa in santas:
        for house in santa.houses:
            houses.add(house)
    return houses

def part2():
    text = open(os.path.join('inputs', 'day03.input')).read()
    instructions = parse(text)
    santas = nsantas(instructions)
    houses = unique_houses(*santas)
    print '%s houses get at leat one present' % (len(houses), )

def main():
    tests()
    part1()
    part2()

if __name__ == '__main__':
    main()
