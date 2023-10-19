import argparse

def number_from_digits(digits, base=10):
    # - benchmarks: it is faster to int(digits_as_string)
    return sum(d * base ** e for e, d in enumerate(reversed(digits)))

def number_from_digits(digits):
    return int(''.join(map(str, digits)))

def to_digits(integer):
    return tuple(map(int, str(integer)))

def torn(digits):
    index = len(digits) // 2
    left_number = number_from_digits(digits[:index])
    right_number = number_from_digits(digits[index:])
    return (left_number + right_number) ** 2

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.add_argument('a', type=int)
    args = parser.add_argument('b', type=int)
    args = parser.parse_args(argv)

    for integer in range(args.a, args.b):
        digits = to_digits(integer)
        if torn(digits) == integer:
            print(integer)

if __name__ == '__main__':
    main()

# 2023-10-18
# https://www.comp.nus.edu.sg/~henz/projects/puzzles/digits/index.html
# Solution:
# /home/hitbox/repos/reference/hakank/hakank/swi_prolog/twin_letters.pl
# /home/hitbox/repos/reference/hakank/hakank/swi_prolog/torn_numbers.pl
# The Torn Number from "Amusements in Mathematics, Dudeney", number 113
# I had the other day in my possession a label bearing the number 3025 in large
# figures. This got accidentally torn in half, so that 30 was on one piece and
# 25 on the other. On looking at these pieces I began to make a calculation,
# scarcely concious of what I was doing, when I discovered this little
# peculiarity. If we add the 30 and the 25 together and square the sum we get
# as the result the complete original number on the label! Now, the puzzle is
# to find another number, composed of four figures, all different, which may be
# divided in the middle and produce the same result.
