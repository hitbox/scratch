#!python
import os

def surface_area(l, w, h):
    return 2*l*w + 2*w*h + 2*h*l

def extra(l, w, h):
    a = [l, w, h]
    a.remove(max(a))
    return a[0] * a[1]

def wrappingpaper(l, w, h):
    return surface_area(l, w, h) + extra(l, w, h)

def faces(l, w, h):
    yield (l, w)
    yield (w, h)
    yield (l, h)

def shortest_distance_around_sides(l, w, h):
    return min( s1 * 2 + s2 * 2 for s1, s2 in faces(l, w, h) )

def cubic_volume(l, w, h):
    return l * w * h

def ribbon(l, w, h):
    return shortest_distance_around_sides(l, w, h) + cubic_volume(l, w, h)

def parseline(line):
    return map(int, line.split('x'))

def parse(text):
    return map(parseline, text.splitlines())

def tests():
    assert wrappingpaper(2, 3, 4) == 58
    assert wrappingpaper(1, 1, 10) == 43
    assert ribbon(2, 3, 4) == 34
    assert ribbon(1, 1, 10) == 14

def part1():
    input = open(os.path.join('inputs', 'day02.input')).read()
    data = parse(input)
    total = sum((wrappingpaper(l, w, h) for l,w,h in data))
    print 'Need %s total square feet.' % total

def part2():
    input = open(os.path.join('inputs', 'day02.input2')).read()
    data = parse(input)
    total = sum((ribbon(l, w, h) for l, w, h in data))
    print 'Total ribbon needed: %s' % total

def main():
    tests()
    part1()
    part2()

if __name__ == '__main__':
    main()
