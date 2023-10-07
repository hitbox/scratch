#!python
import re
from pprint import pprint as pp

from adventlib import input_path

START = 20151125

# 1. is odd
MULBY = 252533

# 1. is prime
# 2. is odd
DIVBY = 33554393

def get_text():
    return open(input_path(__file__, 1)).read()

def get_input():
    text = get_text()
    match = re.search('Enter the code at row (\d+), column (\d+)\.$', text)
    row, column = match.groups()
    row = int(row)
    column = int(column)
    return (row, column)

def naive():
    code = START
    yield code

    while True:
        code = (code * MULBY) % DIVBY
        yield code

def nth(row, column):
    n = 1
    r, c = 1, 1
    while True:
        if (r, c) == (row, column):
            return n
        n += 1
        r += -1
        if r < 1:
            r = c + 1
            c = 1
            continue
        c += 1

def main():

    row_column = get_input()

    n = nth(*row_column)

    codes = naive()

    for _ in xrange(n):
        code = next(codes)

    print code
    #pp(objects)

if __name__ == '__main__':
    main()
