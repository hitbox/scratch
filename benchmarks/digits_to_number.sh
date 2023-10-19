#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

python -m timeit --setup "digits = (1, 2, 3, 4)" -- "sum(d*10**e for e, d in enumerate(reversed(digits)))"

python -m timeit --setup "digits = (1, 2, 3, 4)" -- "int(''.join(map(str, digits)))"
