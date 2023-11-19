#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

# sorted list of words
py_wordlist="words = ['another', 'data', 'date', 'hello', 'text', 'word']"
py_prefix="prefix = 'dat'"

for func_suffix in loop_flavor{1..3} bisect; do
    echo $func_suffix
    python -m timeit \
        --setup "from prefix_search import prefix_search_${func_suffix} as prefix_search" \
        --setup "${py_wordlist}" \
        --setup "${py_prefix}" \
        -- \
        "prefix_search(words, prefix)"
done

# 2023-11-15
# - https://martinheinz.dev/blog/106
# - testing his statement that bisect is faster
# - it is not and the simple loop is easier to understand
