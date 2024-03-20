#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

statement="batched(range(100), 3)"

walrus_batched="from itertools import islice

def batched(iterable, n):
    iterable = iter(iterable)
    while batch := tuple(islice(iterable, n)):
        yield batch"

echo walrus
python -m timeit --setup "${walrus_batched}" -- "${statement}"

legacy_batched="from itertools import islice

def batched(iterable, n):
    iterable = iter(iterable)
    while True:
        batch = tuple(islice(iterable, n))
        if not batch:
            return
        yield batch"

echo legacy
python -m timeit --setup "${legacy_batched}" -- "${statement}"

# 2024-03-20 Wed.
# - curious how fast walrus is
# - apparently comparable--sometimes faster or slower
