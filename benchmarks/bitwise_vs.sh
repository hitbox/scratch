#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

setup="from bitwise import python_add as add"

python -m timeit \
    -s "from bitwise import python_add as add" \
    -- \
    "add(5, 6)"

python -m timeit \
    -s "from bitwise import bitwise_add as add" \
    -- \
    "add(5, 6)"

# 2024-08-21 Wed.
# - This is silly. The interpreter handles + (add) better than it can be
#   reimplemented in Python itself, inside a loop! Of course.
# - I feel like keeping t his anyhow.
