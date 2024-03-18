import unittest

from itertools import product

TESTS = [
    # ((nums, target), expected)
    (([2,3,1], 3), [0, 2]),
]

class TestMixin:

    def test(self):
        for (nums, target), expected in TESTS:
            self.assertEqual(naive(nums, target), expected)


class TestNaive(unittest.TestCase, TestMixin):

    @property
    def algorithm(self):
        return naive


class TestHash(unittest.TestCase, TestMixin):

    @property
    def algorithm(self):
        return hashed


def naive(nums, target):
    for (i, x), (j, y) in product(enumerate(nums), enumerate(nums)):
        if i != j and x + y == target:
            return [i, j]

def hashed(nums, target):
    seen = {}
    for i, value in enumerate(nums):
        remaining = target - value
        if remaining in seen:
            return [i, seen[remaining]]
        else:
            seen[value] = i

# https://nullprogram.com/blog/2023/06/26/
# https://leetcode.com/problems/two-sum/solutions/737092/sum-megapost-python3-solution-with-a-detailed-explanation/
