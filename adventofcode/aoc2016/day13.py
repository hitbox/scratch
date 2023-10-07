import math
import random
from common import astar, path as getpath

class IsOpen(object):

    def __init__(self, favorite):
        self.favorite = favorite

    def __call__(self, x, y):
        a = (x*x + 3*x + 2*x*y + y + y*y) + self.favorite
        ones = sum(1 for c in bin(a) if c == '1')
        return ones % 2 == 0

class Maze(object):

    def __init__(self, isopenfunc):
        self._isopen = isopenfunc
        self.cache = {}

    def isopen(self, x, y):
        if (x, y) not in self.cache:
            self.cache[(x,y)] = self._isopen(x, y)
        return self.cache[(x,y)]

    def iswall(self, x, y):
        if (x,y) not in self.cache:
            self.cache[(x,y)] = not self._isopen(x,y)
        return self.cache[(x,y)]

    def pretty(self, width, height, mark=None):
        pad = '%3s'
        if mark is None:
            mark = set()
        s = '    ' + ''.join(pad % i for i in range(width)) + '\n'
        l = []
        def getchar(x, y):
            return 'O' if (x,y) in mark else '' if self.isopen(x, y) else '#'

        for y in range(height):
            l.append((pad + ' %s') % (y, ''.join(pad % getchar(x, y) for x in range(width))))
        s += '\n'.join(l)
        return s

class Heuristic(object):

    def __init__(self, goal):
        self.goal = goal
        self.gx, self.gy = self.goal

    def __call__(self, point):
        x, y = point
        dx, dy = self.gx - x, self.gy - y
        return math.sqrt(dx * dx + dy * dy)


class Moves(object):

    def __init__(self, maze):
        self.maze = maze

    def __call__(self, point):
        x, y = point
        for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
            tx, ty = (x + dx, y + dy)
            if tx >= 0 and ty >= 0:
                if self.maze.isopen(tx, ty):
                    yield (tx, ty)

def test():
    isopen = IsOpen(10)
    maze = Maze(isopen)
    heuristic = Heuristic((7, 4))
    moves = Moves(maze)

    path = set(astar((1,1), heuristic, moves))
    #print(maze.pretty(10, 7, path))
    assert len(path)-1 == 11

def part1():
    isopen = IsOpen(1358)
    maze = Maze(isopen)

    goal = (31, 39)
    heuristic = Heuristic(goal)
    moves = Moves(maze)

    path = astar((1,1), heuristic, moves)
    print('Day 13, Part 1: %s steps' % (len(path) - 1, ))

    print(maze.pretty(goal[0], goal[1], path))

def part2():
    isopen = IsOpen(1358)
    maze = Maze(isopen)
    moves = Moves(maze)

    forks = {}

    paths = {
        (1,1): {
            (1,2): None,
            (2,1): {
                (2,0): None,
                (3,1): {
                    (3,2): {
                        (4,2): {
                            (5,2): None,
                            (4,3): {
                                (4,4): {
                                    (5,4): None
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    paths = [
        [ (1,1), (1,2) ],
        [ (1,1), (2,1), (2,0) ],
        [ (1,1), (2,1), (3,1), (3,2), (4,2), (5,2) ],
        [ (1,1), (2,1), (3,1), (3,2), (4,2), (4,3), (4,4), (5,4) ],
    ]

    def visit(point, step=0):

        visited.append(point)

        step += 1
        if step > 8:
            return

        neighbors = moves(point)

        if len(neighbors) > 1:
            forks[point] = neighbors
        elif len(neighbors) > 0:
            visit(neighbors, step)

            if neighbor not in visited:
                visit(neighbor, step)

    visit((1,1))
    print(visited)

    best = visited
    width, height = max(p[0] for p in best), max(p[1] for p in best)
    if width < 10:
        width = 10
    if height < 10:
        height = 10
    print(maze.pretty(width, height, best))

    # 110 too low


def main():
    test()
    #part1()
    part2()

if __name__ == '__main__':
    main()
