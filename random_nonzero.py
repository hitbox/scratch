import random
import timeit

def rand_nonzero_recursive(a, b):
    #assert a < 0 < b, 'Range must span zero (negativate to positive)'
    n = random.randint(a, b)
    return n if n != 0 else rand_nonzero_recursive(a, b)

def rand_nonzero_offset(a, b):
    #assert a < 0 < b, 'Range must span zero (negativate to positive)'
    n = random.randint(a, b - 1)
    return n + (1 if n >= 0 else 0)

def print_result(stmt):
    print(stmt)
    result = timeit.repeat(stmt, globals=globals())
    print(f'Best of 5 runs: {min(result):.6f} seconds')

print_result('rand_nonzero_recursive(-1, +1)')
print_result('rand_nonzero_offset(-1, +1)')
