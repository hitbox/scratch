import argparse
import random

def twosum(nums, target):
    pairs = {}
    for i, n in enumerate(nums):
        d = target - n
        print(locals())
        if d in pairs:
            return (i, pairs[d])
        pairs[n] = i

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('target', type=int)
    parser.add_argument('nums', nargs='+', type=int)
    parser.add_argument('--randomize', action='store_true')
    args = parser.parse_args(argv)

    if args.randomize:
        random.shuffle(args.nums)

    print(twosum(args.nums, args.target))

if __name__ == '__main__':
    main()

# https://leetcode.com/problems/two-sum/description/
