#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

a=1e5
b=2

for op in '+' '-' '*' '/' '**'; do
    echo "$a $op $b"
    python -m timeit -s "a = $a" -s "b = $b" -- "a $op b"
done

# 2024-08-11 Sun.
# - How fast is simple arithmetic?
# - Pretty fast it would seem. Exponentiation slowest.
