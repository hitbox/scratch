#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

setup="
import random
import string

d = dict(zip(string.ascii_lowercase, range(len(string.ascii_lowercase))))
"

echo list
python -m timeit --setup "${setup}" -- "random.sample(list(d), 3)"

echo sorted
python -m timeit --setup "${setup}" -- "random.sample(sorted(d), 3)"

# 2024-03-21
# Reason:
# random.sample throws error saying to use sorted
# for speed?
# Result:
# both about the same for speed
