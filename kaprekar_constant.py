import argparse

KAPREKARS_CONSTANT = 6174

def kaprekar_step(number):
    # 1. make four digit, zero-padded string of digits
    # 2. sort ascending and get digits
    # 3. sort descending and get digits
    # 4. convert both sets of digits into integers
    # 5. return their difference
    digits = map(int, f'{number:04d}')
    a, b, c, d = ascending = sorted(digits)
    w, x, y, z = reversed(ascending)
    bigger = (w * 1000 + x * 100 + y * 10 + z)
    smaller = (a * 1000 + b * 100 + c * 10 + d)
    return bigger - smaller

def kaprekar_loop(prev):
    while True:
        next_ = kaprekar_step(prev)
        if next_ == prev:
            assert next_ == KAPREKARS_CONSTANT
            break
        yield (prev, next_)
        prev = next_

def four_digit_number(string):
    string = f'{string:04}'
    if len(string) != 4:
        raise ValueError('Invalid length.')
    if not string.isdigit():
        raise ValueError('Invalid character.')
    if len(set(string)) == 1:
        raise ValueError('Must not be monodigit.')
    return int(string)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'four_digits',
        type = four_digit_number,
        help = (
            'A non-monodigit four digit, integer.'
            ' It is automatically padded with zeros to four digits.',
        ),
    )
    args = parser.parse_args(argv)

    prev = args.four_digits
    for prev, next_ in kaprekar_loop(prev):
        print(f'{prev} -> {next_}')

if __name__ == '__main__':
    main()

# 2024-04-21 Sun.
# https://demian.ferrei.ro/blog/programmer-vs-mathematician
# https://en.wikipedia.org/wiki/6174
# https://en.wikipedia.org/wiki/Repdigit
