#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

setup='d = dict(a=1, b=2, c=3)'

python -m timeit --setup "${setup}" -- "{v:k for k,v in d.items()}"
python -m timeit --setup "${setup}" -- "dict(map(reversed, d.items()))"

# 2024-01-31
# - dict comprehension is almost twice as fast
