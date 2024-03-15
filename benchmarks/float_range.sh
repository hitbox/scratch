#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

test_call="frange(0, 100, 2)"

setup_inner_function="def frange(start, stop=None, step=None):
    if stop is None:
        stop = start
        start = 0.0

    if step is None:
        step = 1.0

    current = float(start)

    def within_range(current, stop, step):
        if step > 0:
            return current < stop
        else:
            return current > stop

    while within_range(current, stop, step):
        yield current
        current += step"

echo inner function
python -m timeit --setup "${setup_inner_function}" -- "${test_call}"

# save anything by avoiding a check?
setup_inner_function2="def frange(start, stop=None, step=None):
    if stop is None:
        stop = start
        start = 0.0

    if step is None:
        step = 1.0

    current = float(start)

    if step > 0:
        def within_range(current, stop, step):
            return current < stop
    else:
        def within_range(current, stop, step):
            return current > stop

    while within_range(current, stop, step):
        yield current
        current += step"

echo inner function 2
python -m timeit --setup "${setup_inner_function2}" -- "${test_call}"

import_operator_function="
import operator as op

def cmp_for_step(step):
    if step < 0:
        return op.gt
    else:
        return op.lt

def frange(start, stop=None, step=None):
    if stop is None:
        stop = start
        start = 0.0

    if step is None:
        step = 1.0

    cmp = cmp_for_step(step)
    current = float(start)
    while cmp(current, stop):
        yield current
        current += step"

echo import operator
python -m timeit --setup "${import_operator_function}" -- "${test_call}"

# 2024-03-15 Fri.
# - first one saves imports and is usually a little bit faster
