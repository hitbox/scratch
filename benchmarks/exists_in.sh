#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

echo "benchmark check existence"

echo set
python -m timeit \
    --setup "data = {2,3}" \
    -- \
    "for i in range(10):" \
    "    i in data"

echo tuple
python -m timeit \
    --setup "data = (2,3)" \
    -- \
    "for i in range(10):" \
    "    i in data"

echo list
python -m timeit \
    --setup "data = [2,3]" \
    -- \
    "for i in range(10):" \
    "    i in data"

# 2023-11-23
# - set looks to be about 50 nsec faster
