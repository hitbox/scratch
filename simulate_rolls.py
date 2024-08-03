import argparse
import random

from collections import Counter
from collections import defaultdict

def roll(sides=6):
    return random.randint(1, sides)

def chi_squared(expected, observed):
    total = 0
    for exp, obs in zip(expected, observed):
        total += (obs - exp) ** 2 / exp
    return total

def simulate_rolls(num_rolls, roll_func=roll):
    histogram = defaultdict(int)
    for _ in range(num_rolls):
        rolled_value = roll_func
        histogram[rolled_value] += 1
    return histogram

def example():
    die_values = range(1,7)

    num_trials = 1000
    num_rolls = 60

    # table linked from article
    # https://greenteapress.com/thinkstats/html/book008.html#toc63
    # sum(values) = num_rolls (60)
    observed = {1: 8, 2: 9, 3: 19, 4: 6, 5: 8, 6: 10}

    # relying on dict insert order
    expected = {die_value: num_rolls/len(die_values) for die_value in die_values}

    threshold = chi_squared(expected.values(), observed.values())

    # count simulated roll trials >= the threshold
    count = 0
    for _ in range(num_trials):
        # count of randomly rolled die values
        simulated = Counter(roll() for _ in range(num_rolls))
        simulated_values = [simulated[face] for face in sorted(simulated)]
        chi2 = chi_squared(expected.values(), simulated_values)
        if chi2 >= threshold:
            count += 1

    pvalue = count / num_trials
    print(f'{count=}, {num_trials=}, {pvalue=}')

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    example()

if __name__ == '__main__':
    main()

# https://allendowney.blogspot.com/2011/05/there-is-only-one-test.html
