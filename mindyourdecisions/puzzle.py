import itertools

# https://www.youtube.com/watch?v=ToIENnaMpLo

statements = [
    ((9, 2, 8, 5), 'one number is correct but in the wrong position'),
    ((1, 9, 3, 7), 'two numbers are correct but in the wrong positions'),
    ((5, 2, 1, 1), 'one number is correct and in the right position'),
    ((6, 5, 0, 7), 'nothing is correct'),
    ((8, 5, 2, 4), 'two number are correct but in the wrong position'),
]

tups = [numtup for numtup, english in statements]

has_correct = set((num for tup in tups for num in tup))

for numtup in itertools.permutations(range(10), 4):
    if any(correct in numtup for correct in has_correct):
        if numtup != tups[3]:
            if any(n == c for n, c in zip(numtup, tups[2])):
                print(numtup)

