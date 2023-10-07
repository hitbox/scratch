#!python2
import re
from adventlib import input_path

line_re = re.compile('(turn on|turn off|toggle) (\d+),(\d+) through (\d+),(\d+)').match

def parse(text, funcmap):
    for line in text.splitlines():
        m = line_re(line)
        if m:
            t = m.groups()
            func = funcmap[t[0]]
            start = map(int, t[1:3])
            end = map(int, t[3:5])
            yield func, start, end

def run(instructions):
    for func, start, end in instructions:
        startx, starty = start
        endx, endy = end
        for x in xrange(startx, endx + 1):
            for y in xrange(starty, endy + 1):
                func((x,y))

def runpart(lights, funcmap, fmtstr, func):
    text = open(input_path(__file__, 1)).read()
    instructions = parse(text, funcmap)
    run(instructions)

    print fmtstr % func(lights)


def part1():
    lights = { (x,y): False for x in xrange(1000) for y in xrange(1000) }

    def on(light):
        lights[light] = True

    def off(light):
        lights[light] = False

    def toggle(light):
        lights[light] = not lights[light]

    funcmap = {
        'turn on': on,
        'turn off': off,
        'toggle': toggle,
    }

    def output(lights):
        return len([v for v in lights.values() if v])

    runpart(lights, funcmap, 'Part 1: lights lit: %s', output)

def part2():
    lights = { (x,y): 0 for x in xrange(1000) for y in xrange(1000) }

    def on(light):
        lights[light] += 1

    def off(light):
        b = lights[light]
        lights[light] = b - 1 if b > 0 else 0

    def toggle(light):
        lights[light] += 2

    funcmap = {
        'turn on': on,
        'turn off': off,
        'toggle': toggle,
    }

    def output(lights):
        return sum(lights.values())

    runpart(lights, funcmap, 'Part 2: total brightness: %s', output)

if __name__ == '__main__':
    part1()
    part2()
