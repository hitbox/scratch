# https://leetcode.com/problems/two-sum/description/
import argparse
import random

def twosum(nums, target):
    pairs = {}
    for i, n in enumerate(nums):
        print(locals())
        if target - n in pairs:
            return [i, pairs[target - n]]
        pairs[n] = i

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('target', type=int)
    parser.add_argument('nums', nargs='+', type=int)
    parser.add_argument('--randomize', action='store_true')
    args = parser.parse_args(argv)

    print(twosum(args.nums, args.target))

if __name__ == '__main__':
    main()
