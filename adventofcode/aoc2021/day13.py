import operator
import re
import textwrap

from itertools import starmap

from util import input_filename

_day13_example = '''\
6,10
0,14
9,10
0,3
10,4
4,11
6,0
6,12
4,1
0,13
10,12
3,4
3,0
8,4
1,10
2,14
8,10
9,0

fold along y=7
fold along x=5'''

_day13_example_render = '''\
...#..#..#.
....#......
...........
#..........
...#....#.#
...........
...........
...........
...........
...........
.#....#.##.
....#......
......#...#
#..........
#.#........'''

_day13_example_firstfold_render = '''\
#.##..#..#.
#...#......
......#...#
#...#......
.#.#..#.###
...........
...........'''

_day13_example_secondfold_render = '''\
#####
#...#
#...#
#...#
#####'''
# NOTE: our renderer excludes two empty lines at the bottom

_dotfold_sep_re = re.compile('^$', flags=re.MULTILINE)
_fold_re = re.compile(r'^fold along ([xy])=(\d+)')

def parse_paper(string):
    dotcoords, folds = _dotfold_sep_re.split(string.strip())
    # process dot coordinates
    dotcoords = set(tuple(map(int, line.split(','))) for line in dotcoords.splitlines())
    # process fold strings
    # XXX: why after split do we have the empty line? hence the `if line`
    folds = [_fold_re.match(line).groups() for line in folds.splitlines() if line]
    folds = [(xy, int(num)) for xy, num in folds]
    return dotcoords, folds

def maximums(dotcoords):
    maxx = max(x for x, y in dotcoords)
    maxy = max(y for x, y in dotcoords)
    return (maxx, maxy)

def render_dotcoords(dotcoords, emptychar='.'):
    maxx, maxy = maximums(dotcoords)
    lines = []
    # +1 because zero is a position
    for y in range(maxy+1):
        line = ''
        for x in range(maxx+1):
            line += '#' if (x,y) in dotcoords else emptychar
        lines.append(line)
    s = '\n'.join(lines)
    return s

def divide(dotcoords, axis, index):
    # NOTE: references name later assigned
    if axis == 'x':
        def pred(x, y):
            return comp(x, index)
    else:
        def pred(x, y):
            return comp(y, index)
    comp = operator.lt
    half1 = set((x,y) for x,y in dotcoords if pred(x,y))
    comp = operator.ge
    half2 = set((x,y) for x,y in dotcoords if pred(x,y))
    return (half1, half2)

def fold(dotcoords, axis, index):
    assert axis in ('x', 'y'), '{axis=} must be x or y.'
    maxx, maxy = maximums(dotcoords)
    half1, half2 = divide(dotcoords, axis, index)
    if axis == 'x':
        def foldcoord(x, y):
            return (maxx - x, y)
    else:
        def foldcoord(x, y):
            return (x, maxy - y)
    folded_half = set(filter(None, starmap(foldcoord, half2)))
    folded = half1.union(folded_half)
    return folded

def _example_1():
    dotcoords, folds = parse_paper(_day13_example)
    render = render_dotcoords(dotcoords)
    assert render == _day13_example_render, 'Dot coordinates render does not match.'
    expect = [('y', 7), ('x', 5)]
    assert folds == expect, f'{folds=} != {expect=}'
    firstfold = fold(dotcoords, *folds[0])
    nvisible = len(firstfold)
    assert nvisible == 17, f'{nvisible=} != 17'
    # second fold
    secondfold = fold(firstfold, *folds[1])
    nvisible = len(secondfold)
    assert nvisible == 16, f'{nvisible=} != 16'
    second_render = render_dotcoords(secondfold)
    assert second_render == _day13_example_secondfold_render

'''
fold y=7

 0: ...#..#..#.
 1: ....#......
 2: ...........
 3: #..........
 4: ...#....#.#
 5: ...........
 6: ...........
 7: ----------- (this line exists and will always be empty)
 8: ...........
 9: ...........
10: .#....#.##.
11: ....#......
12: ......#...#
13: #..........
14: #.#........
'''

def day13_input_string():
    return open(input_filename(13)).read()

def challenge1():
    string = day13_input_string()
    dotcoords, foldarglist = parse_paper(string)
    firstfold = fold(dotcoords, *foldarglist[0])
    nvisible = len(firstfold)
    assert nvisible == 729, f'{nvisible=} != 729'
    print(f'Day 13 Part 1 Solution: {nvisible=}')

def day13_part1():
    """
    Day 13 Part 1
    """
    _example_1()
    challenge1()

def day13_part2():
    """
    """
    _example_1()
    string = day13_input_string()
    dotcoords, foldarglist = parse_paper(string)
    for foldargs in foldarglist:
        dotcoords = fold(dotcoords, *foldargs)
    print('Day 13 Part 2 Solution:')
    render = render_dotcoords(dotcoords, emptychar=' ')
    print(render)

    import pygame
    pygame.display.init()

    maxx, maxy = maximums(dotcoords)
    image = pygame.Surface((maxx, maxy))
    for coord in dotcoords:
        image.set_at(coord, (200,)*3)

    s = 25
    maxx *= s
    maxy *= s
    screen = pygame.display.set_mode((maxx, maxy))

    pygame.transform.scale(image, (maxx, maxy), screen)

    while not pygame.event.peek(pygame.QUIT):
        pygame.display.flip()
