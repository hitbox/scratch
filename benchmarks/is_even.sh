#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

n="1000"

echo "modulo"
python -m timeit -- "for num in range($n):" "  num % 2 == 0"

echo "bitwise"
python -m timeit -- "for num in range($n):" "  (num ^ 1) == (num + 1)"

# 2024-10-17 Thu.
# - Modulo is faster.
