#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

python -m timeit --setup "x = None" -- "bool(x)"

python -m timeit --setup "x = None" -- "x is None"

python -m timeit --setup "x = None" -- "x is not None"

# 2023-12-26
# - `is` is faster by about 5 nsec
# -  `is not` is about the same as `is`
