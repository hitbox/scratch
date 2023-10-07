#!python
import json
import sys
from adventlib import input_path

def isstring(x):
    return isinstance(x, (str, unicode))

def rsum(data, ignore=None, _depth=0):
    if isinstance(data, int):
        return data

    if hasattr(data, 'items') and (ignore is None or not ignore(data)):
        # dict
        return sum( rsum(v, ignore, _depth+1) for k,v in data.items() if not isstring(v))
    else:
        # list
        return sum( rsum(i, ignore, _depth+1) for i in data if not isstring(i))

    return 0

def red(data):
    return "red" in data or "red" in data.values()

def test():
    assert rsum([1,2,3]) == 6
    assert rsum(dict(a=2,b=4)) == 6
    assert rsum([[[3]]]) == 3
    assert rsum(dict(a=dict(b=4),c=-1)) == 3
    assert rsum(dict(a=[-1,1])) == 0
    assert rsum([-1,dict(a=1)]) == 0
    assert rsum([]) == 0
    assert rsum({}) == 0

    assert rsum([1,2,3], ignore=red) == 6
    assert rsum([1,{"c":"red","b":2},3], ignore=red) == 4
    assert rsum({"d":"red","e":[1,2,3,4],"f":5}, ignore=red) == 0
    assert rsum([1,"red",5], ignore=red) == 6

def main():
    with open(input_path(__file__, 1)) as f:
        data = json.load(f)
        print 'Part 1: %s' % rsum(data)
        print 'Part 2: %s' % rsum(data, ignore=red)

if __name__ == '__main__':
    test()
    main()
