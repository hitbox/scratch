#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

echo "calc everytime"
python -m timeit \
    --setup "import math" \
    -- \
    "math.pi / 2"

echo "name lookup"
python -m timeit \
    --setup "import math" \
    --setup "half_pi = math.pi / 2" \
    -- \
    "half_pi"

echo "rect calc"
python -m timeit \
    --setup "rect = (0, 0, 10, 10)" \
    -- \
    "x, y, w, h = rect" \
    "(x, y)" \
    "(x + w, y)" \
    "(x + w, y + h)" \
    "(x, y + h)"

echo "rect pre-calc"
python -m timeit \
    --setup "rect = (0, 0, 10, 10)" \
    -- \
    "x, y, w, h = rect" \
    "r = x + w" \
    "b = y + h" \
    "(x, y)" \
    "(r, y)" \
    "(r, b)" \
    "(x, b)"


# 2023-12-28
# - name lookup is nearly four times faster.
# - kinda like duh.
# 2024-04-03
# - pre-calculating right and bottom improves speed by about 30 nsec
