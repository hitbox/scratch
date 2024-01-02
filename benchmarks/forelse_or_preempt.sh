#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

python -m timeit \
    "for i in range(10):" \
    "    if i == 10:" \
    "        r = 10" \
    "        break" \
    "else:" \
    "    r = None" \
    "assert r is None"

python -m timeit \
    "r = None" \
    "for i in range(10):" \
    "    if i == 10:" \
    "        r = i" \
    "        break" \
    "assert r is None"

# 2024-01-01
# - effectively the same speed
# - use most clear
