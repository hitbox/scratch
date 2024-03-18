import argparse
import itertools as it
import operator as op

def consecutive(items, ordering=None):
    if ordering is None:
        ordering = lambda x: x
    grouped = it.groupby(
        enumerate(items),
        key = lambda x: x[0] - ordering(x[1])
    )
    for key, group in grouped:
        yield map(op.itemgetter(1), group)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('type', type=eval)
    parser.add_argument('items', nargs='+')
    parser.add_argument('--ordering')
    args = parser.parse_args(argv)
    print(args)

    if args.ordering:
        ordering = eval(args.ordering)
    else:
        ordering = args.ordering

    items = map(args.type, args.items)
    for group in consecutive(items, ordering):
        print(list(group))

if __name__ == '__main__':
    main()

# - incident-73949-supply-chain-update-vendor-names
# - want to reduce the giant IN statement
