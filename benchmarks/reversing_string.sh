#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

setup="string = 'banana'"

echo slice
python -m timeit --setup "${setup}" -- "string[::-1]"

echo reverse and join
python -m timeit --setup "${setup}" -- "''.join(reversed(string))"

echo lambda slice
python -m timeit --setup "${setup}" \
    --setup "reverse_string = lambda string: string[::-1]" \
    -- "string[::-1]"

echo function slice
python -m timeit --setup "${setup}" \
    --setup "def reverse_string(string):" \
    --setup "    return string[::-1]" \
    -- "string[::-1]"

# 2024-06-30
# - slice is much faster of course
# - want to have something fast for a sort or group key function
# - lambda- and function-slice as fast as slice
