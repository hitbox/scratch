def combinations(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        # Scan indices right-to-left until finding one that is not at its
        # maximum (i + n - r).
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            # indices are all at their maximum value, done
            return

        # Increment the current index which we know is not at its maximum. Then
        # move back to the right setting each index to its lowest possible
        # value (one higher than the index to its left -- this maintains the
        # sort order invariant).
        indices[i] += 1
        j = i + 1
        while j < r:
            indices[j] = indices[j-1] + 1
            j += 1

        yield tuple(pool[i] for i in indices)

print(list(combinations('ABC', 2)))
import itertools as it
print(list(it.combinations('ABC', 2)))

# 2024-02-03
# - working through 3Sum on leetcode
# https://leetcode.com/problems/3sum/
# - trying to avoid importing itertools
# - recreated itertools.combinations from the cpython code
# - could have looked it up in the docs
# https://docs.python.org/3/library/itertools.html#itertools.combinations
# - oh well
# - maybe an algorithm like this supplemented with the constraints of 3Sum
#   would work?
