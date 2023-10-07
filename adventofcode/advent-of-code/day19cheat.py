#https://www.reddit.com/r/adventofcode/comments/3xflz8/day_19_solutions/cy4cu5b
from random import shuffle

text = open('inputs/day19.input').read()

#reps = [('Al', 'ThF), ...]
reps = [line.split(' => ') for line in text.splitlines()[:-1] if line]
mol = text.splitlines()[-1]

target = mol
part2 = 0

while target != 'e':
    tmp = target
    for a, b in reps:
        if b not in target:
            continue

        target = target.replace(b, a, 1)
        part2 += 1

    if tmp == target:
        target = mol
        part2 = 0
        shuffle(reps)

print part2
