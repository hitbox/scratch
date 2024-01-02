#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

python -m timeit "list(map(str, range(100)))"

python -m timeit "[str(i) for i in range(100)]"

# 2023-12-21
# - list comprehension is one microsecond faster!
