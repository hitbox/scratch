#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

for e in {1..5}; do
    echo "add one to int(9e${e})"
    setup="count = int(9e${e})" 
    python -m timeit --setup $setup -- "count + 1"
done

# 2024-06-30
# - After 1000 or so, Python doubles to time to add one
