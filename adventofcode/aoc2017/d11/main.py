import os
import math

dirs = {"ne": (1,-1,0), "n": (0,-1,1), "nw": (-1,0,1), "sw": (-1,1,0), "s": (0,1,-1), "se": (1,0,-1)}

def distance(x, y, z):
    x, y, z = map(abs, (x,y,z))
    return math.floor((x + y + z)/2)

def steps(path):
    x, y, z = 0, 0, 0
    for step in path:
        dx, dy, dz = dirs[step]
        x += dx
        y += dy
        z += dz
    return distance(x, y, z)

def furthest(path):
    maxd = 0
    x, y, z = 0, 0, 0
    for step in path:
        dx, dy, dz = dirs[step]
        x += dx
        y += dy
        z += dz
        d = distance(x,y,z)
        if d > maxd:
            maxd = d
    return maxd

def tests():
    assert steps("ne,ne,ne".split(",")) == 3
    assert steps("ne,ne,sw,sw".split(",")) == 0
    assert steps("ne,ne,s,s".split(",")) == 2
    assert steps("se,sw,se,sw,sw".split(",")) == 3

def get_input():
    return open(os.path.join(os.path.dirname(__file__), "input.txt")).read().strip().split(",")

def main():
    tests()

    # 865 too high
    # 932 too high (of course but I wanted to make sure)

    print("part 1: %s" % (steps(get_input())))
    print("part 2: %s" % (furthest(get_input())))

    # this state solved the puzzles. had to cheat and goto https://www.redblobgames.com/grids/hexagons/
    # been there before but I made a solid attempt to workout the cube coord system on my own.
    # what I don't understand is the distance formula. should I be able to use sqrt(x^2 + y^2 + z^2)?
    # instead it's just divide by 2

if __name__ == "__main__":
    main()
