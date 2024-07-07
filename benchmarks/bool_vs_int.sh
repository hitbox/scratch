#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

python -m timeit --setup "oscillator = True" -- "oscillator = not oscillator"

python -m timeit --setup "oscillator = 0" -- "oscillator = (oscillator + 1) % 1"

# 2024-07-07 Sun.
# - bool faster than int?
# - yes, nearly twice as fast.
