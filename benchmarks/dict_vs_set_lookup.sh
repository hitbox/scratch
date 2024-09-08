#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

echo "test in set"
python -m timeit -s "entities = set(range(int(1e3)))" -s "i = int(999)" -- "i in entities"

echo "test in dict"
python -m timeit \
    -s "from itertools import cycle" \
    -s "r = range(int(1e3))" \
    -s "entities = dict(zip(r, r))" \
    -s "i = int(999)" \
    -- \
    "i in entities"

# 2024-09-08 Sun.
# - Thinking about ECS.
# - Was looking into a database pattern that is essentially ECS.
# - Thinking sets are no good because you lose the mapping to attributes.
# - But a set could scrape back several nsec for testing existence.
