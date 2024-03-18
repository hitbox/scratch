import argparse

def chunked(indexable, n):
    for i in range(0, len(indexable), n):
        yield indexable[i:i+n]

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('n', type=int)
    parser.add_argument('list', nargs='*')
    args = parser.parse_args(argv)

    print(list(chunked(args.list, args.n)))

if __name__ == '__main__':
    main()

# 2023-12-05
# - advent of code 2023, day 5
# - needed to chunk four numbers into twos
# - saw other peoples' stuff
# - loop over the starting indexes and step by n-chunks, slicing
#   https://www.reddit.com/r/adventofcode/comments/18b4b0r/2023_day_5_solutions/kc67hwt/
# - a zip solution
#   https://pastebin.com/6CB1NbQ6
# - went with a itertools groupby solution that still requires and indexable.
#   it uses integer division as the key
# - want a nice solution like more-itertools
# 1. take any iterable
# 2. option for what container to yield, that is allow lists, sets, more
#    iterables.
# - looking to make something that's "quick and dirty" that, at the most,
#   requires only stdlib, satisfies 1 and 2 above.
