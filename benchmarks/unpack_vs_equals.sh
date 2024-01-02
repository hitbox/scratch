#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

python -m timeit "a, b = 0, 0"

python -m timeit "a = b = 0"

# 2024-01-01
# - equals beats unpack by a couple nsec.
