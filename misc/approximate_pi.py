import math

from pprint import pprint
from fractions import Fraction
from itertools import permutations

odds = range(1, 100_000_000, 2)

a = math.pi - 0.000001
b = math.pi + 0.000001

approx = set((i, j) for i, j in permutations(odds, 2) if i > j and a < i / j < b)

def key(item):
    i, j = item
    pi_closeness = abs(math.pi - i / j)
    return (pi_closeness, math.log10(i), math.log10(j))

result = sorted(approx, key=key)

pprint(result[:20])

