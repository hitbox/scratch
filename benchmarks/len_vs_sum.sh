#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

echo "len of container"
python -m timeit -- "len(tuple(i for i in range(100) if i % 2 == 0))"

echo "sum of 1's"
python -m timeit -- "sum(1 for i in range(100) if i % 2 == 0)"

# 2024-03-30
# len of container vs sum(1 ...)
# sum is slight faster
