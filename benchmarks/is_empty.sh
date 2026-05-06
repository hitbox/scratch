#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

echo 'with l = []'
echo "benchmarking if l"
python -m timeit -s 'l = []' -- 'if l: pass'

echo 'with l = ["a", "b", "c"]'
echo "benchmarking if l"
python -m timeit -s 'l = ["a", "b", "c"]' -- 'if l: pass'

echo 'with l = []'
echo "benchmarking if len(l)"
python -m timeit -s 'l = []' -- 'if len(l): pass'

echo 'with l = ["a", "b", "c"]'
echo "benchmarking if len(l)"
python -m timeit -s 'l = ["a", "b", "c"]' -- 'if len(l): pass'

# Using len() doubles the time to run.
