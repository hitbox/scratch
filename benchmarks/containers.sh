#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

setup_generate="g = range(100)"
unit="usec"

echo tuple
python -m timeit --unit "${unit}" --setup "${setup_generate}" -- "tuple(g)"

echo list
python -m timeit --unit "${unit}" --setup "${setup_generate}" -- "list(g)"

echo set
python -m timeit --unit "${unit}" --setup "${setup_generate}" -- "set(g)"

# 2024-03-18 Mon.
# - comparing how fast the builtin containers are
# - tuple() is a little faster than list()
# - why is set so slow? probably from making the items unique.
