#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

a=1
b=3
for x in {0,2,4}; do
    echo "x=$x"

    echo "if-elif-return"
    python -m timeit \
        -s "def clamp(x, a, b):" \
        -s "  if x < a:" \
        -s "    return a" \
        -s "  elif x > b:" \
        -s "    return b" \
        -s "  return x" \
        -- \
        "clamp($x, $a, $b)"

    echo "max(min(...))"
    python -m timeit \
        -s "def clamp(x, a, b):" \
        -s "  return max(a, min(b, x))" \
        -- \
        "clamp($x, $a, $b)"

done

# 2024-08-07
# - Which is fastest clamp method?
# - if-elif-return is 3-4 times faster.
