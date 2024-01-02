#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

python -m timeit \
    --setup "import math" \
    -- \
    "math.pi / 2"

python -m timeit \
    --setup "import math" \
    --setup "half_pi = math.pi / 2" \
    -- \
    "half_pi"

# 2023-12-28
# - name lookup is nearly four times faster.
# - kinda like duh.
