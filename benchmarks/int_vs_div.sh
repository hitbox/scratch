#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

echo "... // 1"
python -m timeit -s "import random" -- "random.random() // 1"

echo "int()"
python -m timeit -s "import random" -- "int(random.random())"

# 2024-09-22 Sun.
# - Came across (...) // 1 to make integer.
# - Is that faster than int(...)?
# - int() is slightly slower, probably function calls again.
