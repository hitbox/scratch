#!python
import argparse
from md5 import md5
from adventlib import parseargs

def gethash(key, n):
    return md5(key + str(n)).hexdigest()

def pred_five_zeros(hash):
    return hash.startswith('0' * 5)

def find_first(key, pred):
    n = 1
    while True:
        hash = gethash(key, n)
        if pred(hash):
            break
        n += 1

    return n, hash

def tests():
    assert find_first('abcdef', pred_five_zeros)[0] == 609043
    assert find_first('pqrstuv', pred_five_zeros)[0] == 1048970

def part1():
    key = 'yzbqklnj'
    n, hash = find_first(key, pred_five_zeros)
    print 'Part 1: %s start with five zeros.' % n

def pred_six_zeros(hash):
    return hash.startswith('0' * 6)

def part2():
    key = 'yzbqklnj'
    n, hash = find_first(key, pred_six_zeros)
    print 'Part 2: %s start with six zeros.' % n

def main():
    args = parseargs()

    if args.test:
        tests()
    elif args.part:
        eval('part%s' % args.part)()
    else:
        part1()
        part2()

if __name__ == '__main__':
    main()
