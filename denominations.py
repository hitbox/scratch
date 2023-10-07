import argparse

from collections import Counter
from decimal import Decimal

denominations = {
    10_000: 'hundred',
    5_000: 'fifty',
    2_000: 'twenty',
    1_000: 'ten',
    500: 'five',
    100: 'dollar',
    25: 'quarter',
    10: 'dime',
    5: 'nickle',
    1: 'penny',
}

def denominate(amount):
    def divisible(denom):
        return denom <= remaining
    denoms = []
    while (total := sum(denoms)) < amount:
        remaining = amount - total
        denom = max(filter(divisible, denominations))
        denoms.append(denom)
    return denoms

def main(argv=None):
    """
    Count change.
    """
    parser = argparse.ArgumentParser(
        description = main.__doc__,
    )
    parser.add_argument('bill', type=Decimal)
    parser.add_argument('given', type=Decimal)
    args = parser.parse_args(argv)

    # convert to pennies
    bill_pennies = args.bill.shift(2)
    given_pennies = args.given.shift(2)

    change = given_pennies - bill_pennies
    if change < 0:
        parser.error('does not cover bill')
    elif change == 0:
        print('exact given')

    returned = denominate(change)
    counted = Counter(returned)

    print(args.given - args.bill)
    print('\n'.join(f'{n} x {denominations[r]}' for r, n in counted.items()))

if __name__ == '__main__':
    main()
