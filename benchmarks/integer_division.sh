#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

python -m timeit "2 / 2"
python -m timeit "2 // 2"

# 2024-01-16
# - very slightly, fraction of a nsec, slower integer division
