#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

nitems="100"
nappends="100"

echo "list.append"
python \
    -m timeit \
    --setup "l = list(range(${nitems}))" \
    -- \
    "for i in range(${nappends}):" \
    "  l.append(i)"

echo "l = list.append"
python \
    -m timeit \
    --setup "l = list(range(${nitems}))" \
    --setup "append = l.append" \
    -- \
    "for i in range(${nappends}):" \
    "  append(i)"

# consistently several 10ths of usec slower!
#
# pygame is losing the readability of their code AND losing performance
