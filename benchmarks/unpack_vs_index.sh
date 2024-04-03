#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

setup="rect = (0, 0, 10, 10)"

echo unpack
python -m timeit --setup "${setup}" -- "_, _, w, h = rect" "w * h"

echo "index access"
python -m timeit --setup "${setup}" -- "rect[2] * rect[3]"

# 2024-04-03
# - given something like a rect, is unpacking horrible for performance?
# - lose a couple nanoseconds
