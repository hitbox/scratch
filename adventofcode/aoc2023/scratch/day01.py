import re
import sys

digit_names = [None, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
digits_re = re.compile('|'.join(['\d'] + digit_names[1:]))

def solve(line, with_names=False):
    digits = digits_re.findall(line)
    if with_names:
        digits = [
            str(digit_names.index(item)) if item in digit_names else item
            for item in digits
        ]
    return int(digits[0] + digits[-1])

total1 = total2 = 0
for line in map(str.strip, sys.stdin):
    total1 += solve(line)
    total2 += solve(line, with_names=True)

print(f'{total1=}')
print(f'{total2=}')
